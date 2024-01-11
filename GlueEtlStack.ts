import * as cdk from 'aws-cdk-lib';
import * as glue from 'aws-cdk-lib/aws-glue';
import * as iam from 'aws-cdk-lib/aws-iam';

class GlueJobStack extends cdk.Stack {
  constructor(scope: cdk.Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // Define a Glue Job
    const glueJob = new glue.CfnJob(this, 'MyGlueJob', {
      command: {
        name: 'pythonshell',
        scriptLocation: 's3://your-bucket/your-python-script.py', // Replace with your S3 path to the Python script
      },
      role: this.createGlueJobRole(),
    });

    // Run the Glue Job on a schedule (e.g., every day at midnight)
    new glue.CfnJobRun(this, 'MyGlueJobRun', {
      jobName: glueJob.ref,
      allocatedCapacity: 10,
      arguments: {
        '--param1': 'value1',
        // Add any additional parameters your Python script expects
      },
      maxCapacity: 20,
      timeout: 2880, // Timeout in minutes
      timeoutType: 'DURATION',
      executionProperty: {
        maxConcurrentRuns: 1,
      },
      notificationProperty: {
        notifyDelayAfter: 0,
      },
      securityConfiguration: 'default', // Use 'default' or replace with your security configuration
    });

    // You may add more configurations based on your specific requirements
  }

  private createGlueJobRole(): iam.Role {
    // Define an IAM role for the Glue Job
    const role = new iam.Role(this, 'MyGlueJobRole', {
      assumedBy: new iam.ServicePrincipal('glue.amazonaws.com'),
    });

    // Attach policies to the role
    role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('service-role/AWSGlueServiceRole'));

    // Add additional policies if needed
    // role.addManagedPolicy(iam.ManagedPolicy.fromAwsManagedPolicyName('AmazonS3ReadOnlyAccess'));

    return role;
  }
}

const app = new cdk.App();
new GlueJobStack(app, 'GlueJobStack');
