import os
import gzip
import pandas as pd
import numpy as np
from fitparse import FitFile
import logging

class FitFileProcessor:
    """
    A class to process .fit.gz files containing activity data and convert them into structured DataFrames.

    Attributes:
        data_dir (str): The directory containing the .fit.gz files to process.
        output_dir (str): The directory to save logs and processed outputs.
        key_fields (list): List of relevant fields to extract from the FIT files.
        file_dtypes (dict): Data types for the resulting DataFrame columns.
        all_data (list): Accumulated data from processed files.
    """

    def __init__(self, data_dir, output_dir):
        """
        Initializes the FitFileProcessor with input and output directories.

        Args:
            data_dir (str): Path to the directory containing .fit.gz files.
            output_dir (str): Path to the directory to save logs and processed outputs.
        """
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.key_fields = [
            "timestamp", "heart_rate", "distance", "cadence", "enhanced_altitude",
            "enhanced_speed", "temperature", "position_lat", "position_long", "power",
            "total_calories", "total_ascent"
        ]
        self.file_dtypes = {
            'workout_id': 'str',
            'elapsed_time': 'float64',
            'distance': 'float64',
            'speed': 'float64',
            'heartrate': 'float64',
            'cadence': 'float64',
            'altitude': 'float64',
            'latitude': 'float64',
            'longitude': 'float64',
            'power': 'float64',
            'total_calories': 'float64',
            'total_ascent': 'float64'
        }
        self.all_data = []
        os.makedirs(output_dir, exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(os.path.join(output_dir, "processing.log")),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger()

    @staticmethod
    def convert_to_decimal_degrees(value):
        """
        Converts a raw latitude/longitude value to decimal degrees.

        Args:
            value (int): The raw latitude/longitude value.

        Returns:
            float: The value converted to decimal degrees.
        """
        return value / 2147483648.0 * 180

    def process_file(self, filepath):
        """
        Processes a single .fit or .fit.gz file and extracts relevant activity data into a DataFrame.

        Args:
            filepath (str): The path to the .fit or .fit.gz file.

        Returns:
            pd.DataFrame: A DataFrame containing the processed data from the file.
        """
        try:
            # Support both .fit and .fit.gz files
            if filepath.endswith(".fit.gz"):
                with gzip.open(filepath, "rb") as fit_stream:
                    fitfile = FitFile(fit_stream.read())  # read into memory
            elif filepath.endswith(".fit"):
                with open(filepath, "rb") as fit_stream:
                    fitfile = FitFile(fit_stream.read())  # read into memory

            else:
                self.logger.warning(f"Unsupported file format: {filepath}")
                return pd.DataFrame()

            activity_type = None
            for record in fitfile.get_messages("sport"):
                for field in record:
                    if field.name == "sport":
                        activity_type = field.value
                        break

            self.logger.info(f"Processing file: {os.path.basename(filepath)} (Activity: {activity_type})")

            file_data = []
            for record in fitfile.get_messages():
                record_data = {"activity_type": activity_type, "file_name": os.path.basename(filepath)}
                for field in record:
                    if field.name.lower() in [key.lower() for key in self.key_fields]:
                        record_data[field.name.lower()] = field.value

                if len(record_data) > 2:
                    file_data.append(record_data)

            file_df = pd.DataFrame(file_data)
            for field in self.key_fields:
                if field.lower() not in file_df.columns:
                    file_df[field.lower()] = 0 if field != "timestamp" else pd.NaT

            if "timestamp" in file_df.columns:
                file_df["timestamp"] = pd.to_datetime(file_df["timestamp"], errors="coerce")
                if file_df["timestamp"].notna().any():
                    file_df["elapsed_time"] = (
                        (file_df["timestamp"] - file_df["timestamp"].min()).dt.total_seconds()
                    ).fillna(0).astype(int)
                else:
                    file_df["elapsed_time"] = 0

            # Remove both extensions
            workout_id = os.path.basename(filepath).replace(".fit.gz", "").replace(".fit", "")
            file_df["workout_id"] = workout_id

            rename_columns = {
                "enhanced_altitude": "altitude",
                "enhanced_speed": "speed",
                "position_lat": "latitude",
                "position_long": "longitude",
                "heart_rate": "heartrate",
            }

            file_df.rename(columns=rename_columns, inplace=True)

            column_order = [
                "workout_id", "timestamp", "elapsed_time", "distance", "speed",
                "heartrate", "cadence", "altitude", "latitude", "longitude",
                "power", "total_calories", "total_ascent"
            ]

            for col in column_order:
                if col not in file_df.columns:
                    file_df[col] = np.nan if col != "timestamp" else pd.NaT

            file_df = file_df[column_order]
            file_df['total_calories'] = np.nanmax(file_df['total_calories'])
            file_df['total_ascent'] = 0 if file_df['total_ascent'].isna().all() else np.nanmax(file_df['total_ascent'])
            file_df['sport_type'] = activity_type

            if "latitude" in file_df.columns:
                file_df["latitude"] = file_df["latitude"].apply(self.convert_to_decimal_degrees)
            if "longitude" in file_df.columns:
                file_df["longitude"] = file_df["longitude"].apply(self.convert_to_decimal_degrees)

            file_df = file_df.astype(self.file_dtypes)
            self.all_data.extend(file_df.to_dict("records"))
            return file_df
        except Exception as e:
            self.logger.error(f"Error processing file {os.path.basename(filepath)}: {e}")
            return pd.DataFrame()

    def process_directory(self, file_name=False):
        """
        Processes all .fit.gz and .fit files in the specified directory and combines their data into a single DataFrame.

        Returns:
            pd.DataFrame: A DataFrame containing combined data from all processed files.
        """
        all_dfs = []
        for filename in os.listdir(self.data_dir):
            filepath = os.path.join(self.data_dir, filename)
            if os.path.isfile(filepath) and (filename.endswith(".fit.gz") or filename.endswith(".fit")):
                file_df = self.process_file(filepath)
                if not file_df.empty:
                    all_dfs.append(file_df)

        if all_dfs:
            combined_df = pd.concat(all_dfs, ignore_index=True)
            combined_df = combined_df.astype(self.file_dtypes)
            if not combined_df.empty:
                combined_df['power'] = combined_df['power'].fillna(0).astype(int)
                combined_df = combined_df.drop_duplicates(subset=['workout_id', 'timestamp']).dropna(subset=['timestamp'])
            self.logger.info("Processing complete. Returning combined DataFrame.")
            if file_name:
                # Rename columns before saving
                combined_df.rename(columns={
                    "power": "watts",
                    "elapsed_time": "time"
                }, inplace=True)

                csv_path = os.path.join(self.output_dir, f"{file_name}.csv")
                combined_df.to_csv(csv_path, index=False)
                self.logger.info(f"Saved DataFrame to {csv_path}")
            return combined_df
        else:
            self.logger.warning("No valid data processed. Returning empty DataFrame.")
            return pd.DataFrame()


# Example usage
if __name__ == "__main__":
    data_dir = "/Users/joshuagordon/Documents/sandbox/strava-im-estimator/ironman-estimator/example_data/"  #dirctory with fit.gz files
    output_dir = "/Users/joshuagordon/Documents/sandbox/strava-im-estimator/ironman-estimator/example_data/"
    file_name = 'test'
    processor = FitFileProcessor(data_dir, output_dir)
    result_df = processor.process_directory(file_name)
