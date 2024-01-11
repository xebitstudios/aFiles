import * as cdk from 'aws-cdk-lib';
import * as glue from 'aws-cdk-lib/aws-glue';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as iam from 'aws-cdk-lib/aws-iam';

class GlueJobStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // DynamoDB Table
    const dynamoTable = new dynamodb.Table(this, 'MyDynamoTable', {
      partitionKey: { name: 'id', type: dynamodb.AttributeType.STRING },
      removalPolicy: cdk.RemovalPolicy.DESTROY, // For demo purposes, consider a more suitable removal policy
    });

    // Glue Job Role
    const glueJobRole = new iam.Role(this, 'MyGlueJobRole', {
      assumedBy: new iam.ServicePrincipal('glue.amazonaws.com'),
    });

    glueJobRole.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSGlueServiceRole'));

    // Allow Glue Job to read from the JDBC database
    // Make sure to replace 'your-jdbc-endpoint', 'your-database-name', 'your-username', 'your-password'
    const connectionProperties = {
      CONNECTION_URL: 'jdbc:mysql://your-jdbc-endpoint:3306/your-database-name',
      USERNAME: 'your-username',
      PASSWORD: 'your-password',
    };

    const rdsAccessPolicy = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      actions: ['rds-db:connect'],
      resources: ['arn:aws:rds-db:region:account-id:dbuser:db-instance-id/your-username'],
      conditions: {
        StringEquals: {
          'rds:db-name': 'your-database-name',
          'rds:hostname': connectionProperties.CONNECTION_URL.split('//')[1],
        },
      },
    });

    glueJobRole.addToPolicy(rdsAccessPolicy);

    // Define Glue Job
    const glueJob = new glue.CfnJob(this, 'MyGlueJob', {
      command: {
        name: 'pythonshell',
        scriptLocation: 's3://your-bucket/your-python-script.py', // Replace with your S3 path to the Python script
      },
      role: glueJobRole.roleArn,
      connections: {
        connections: ['your-jdbc-connection-name'],
      },
      defaultArguments: {
        '--DYNAMO_TABLE_NAME': dynamoTable.tableName,
      },
    });

    // Run Glue Job on-demand
    new glue.CfnJobRun(this, 'MyGlueJobRun', {
      jobName: glueJob.ref,
      arguments: {
        '--param1': 'value1',
        // Add any additional parameters your Python script expects
      },
      notificationProperty: {
        notifyDelayAfter: 0,
      },
      securityConfiguration: 'default', // Use 'default' or replace with your security configuration
    });
  }
}

const app = new cdk.App();
new GlueJobStack(app, 'GlueJobStack');
