from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lower, regexp_replace

def run_etl():
    # M2 Mac optimized Spark Session
    spark = SparkSession.builder \
        .appName("ClinicalTrialETL") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()

    # Load your specific dataset.csv
    try:
        # header=True handles the first row as column names
        df = spark.read.csv("data/dataset.csv", header=True, inferSchema=True)
        
        # Clean and rename columns based on your CSV structure
        cleaned_df = df.select(
            col("NCT Number").alias("id"),
            col("Study Title").alias("title"),
            lower(col("Brief Summary")).alias("summary"),
            col("Conditions"),
            col("Interventions")
        ).withColumn("summary_clean", regexp_replace(col("summary"), "<[^>]*>", ""))

        # Save to Parquet format (efficient for Phase 2)
        cleaned_df.write.mode("overwrite").parquet("data/processed_trials.parquet")
        print("✅ ETL Complete: Saved to data/processed_trials.parquet")
    except Exception as e:
        print(f"❌ Error: {e}. Ensure dataset.csv is in the data folder.")

if __name__ == "__main__":
    run_etl()