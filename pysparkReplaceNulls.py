from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize a Spark session
spark = SparkSession.builder.appName("ReplaceNullWithEmptyString").getOrCreate()

# Example DataFrame with null values
data = [("John", 25, None), ("Alice", None, 30), ("Bob", 28, 35)]
columns = ["Name", "Age", "Score"]
df = spark.createDataFrame(data, columns)

# Show the original DataFrame
print("Original DataFrame:")
df.show()

# Replace null values with empty strings
df_filled = df.fillna("", subset=df.columns)

# Show the DataFrame after replacing null values with empty strings
print("DataFrame after replacing null values with empty strings:")
df_filled.show()

# Stop the Spark session
spark.stop()
