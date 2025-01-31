import pandas as pd
import logging
import sqlite3

class DataCleaner:
    def __init__(self, db_name='telegram_data.db'):
        self.db_name = db_name
        self.cleaned_data = None

        # Initialize logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='data_cleaning.log'
        )

    def load_data(self):
        """Load data from the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_name)
            query = "SELECT * FROM messages"
            df = pd.read_sql_query(query, conn)
            conn.close()
            logging.info("Data loaded successfully.")
            return df
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return None

    def remove_duplicates(self, df):
        """Remove duplicate rows from the DataFrame."""
        try:
            df = df.drop_duplicates()
            logging.info("Duplicates removed successfully.")
            return df
        except Exception as e:
            logging.error(f"Error removing duplicates: {e}")
            return df

    def handle_missing_values(self, df):
        """Handle missing values in the DataFrame."""
        try:
            df['message'].fillna('', inplace=True)  # Fill missing messages with empty string
            df['media_url'].fillna('', inplace=True)  # Fill missing media URLs with empty string
            logging.info("Missing values handled successfully.")
            return df
        except Exception as e:
            logging.error(f"Error handling missing values: {e}")
            return df

    def standardize_formats(self, df):
        """Standardize formats in the DataFrame."""
        try:
            df['date'] = pd.to_datetime(df['date'])  # Convert date to datetime format
            logging.info("Formats standardized successfully.")
            return df
        except Exception as e:
            logging.error(f"Error standardizing formats: {e}")
            return df

    def validate_data(self, df):
        """Validate data to ensure it meets certain criteria."""
        try:
            # Example validation: Ensure all messages are strings
            df['message'] = df['message'].astype(str)
            logging.info("Data validated successfully.")
            return df
        except Exception as e:
            logging.error(f"Error validating data: {e}")
            return df

    def save_cleaned_data(self, df, table_name='cleaned_messages'):
        """Save cleaned data to the SQLite database."""
        try:
            conn = sqlite3.connect(self.db_name)
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            conn.close()
            logging.info("Cleaned data saved successfully.")
        except Exception as e:
            logging.error(f"Error saving cleaned data: {e}")

    def clean_data(self):
        """Run the entire data cleaning pipeline."""
        df = self.load_data()
        if df is not None:
            df = self.remove_duplicates(df)
            df = self.handle_missing_values(df)
            df = self.standardize_formats(df)
            df = self.validate_data(df)
            self.save_cleaned_data(df)
            self.cleaned_data = df
            logging.info("Data cleaning pipeline completed.")
        else:
            logging.error("Data cleaning pipeline failed due to missing data.")