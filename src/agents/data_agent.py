import pandas as pd
import yaml
import os

from src.utils.cleaner import DataCleaner


class DataAgent:
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, "r") as f:
            self.config = yaml.safe_load(f)

        self.cleaner = DataCleaner()

        self.data_path = self.config["paths"]["data"]
        self.thresholds = self.config["thresholds"]

    def load_data(self):
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"Dataset not found at: {self.data_path}")

        df = pd.read_csv(self.data_path)
        df = self.cleaner.clean_dataframe(df)

        return df

    def summarize_daily(self, df):
        return df.groupby("date").agg({
            "spend": "sum",
            "impressions": "sum",
            "clicks": "sum",
            "purchases": "sum",
            "revenue": "sum",
            "ctr": "mean",
            "roas": "mean"
        }).reset_index().to_dict(orient="records")

    def summarize_by_creative(self, df):
        # FIXED: Include creative_message and campaign_name
        creative_summary = df.groupby("creative_type").agg({
            "ctr": "mean",
            "roas": "mean",
            "spend": "sum",
            "impressions": "sum",
            "creative_message": "first",     # FIX
            "campaign_name": "first"         # FIX
        }).reset_index()

        return creative_summary.to_dict(orient="records")

    def summarize_by_audience(self, df):
        return df.groupby("audience_type").agg({
            "ctr": "mean",
            "roas": "mean",
            "spend": "sum",
            "impressions": "sum"
        }).reset_index().to_dict(orient="records")

    def get_low_ctr_ads(self, df):
        threshold = self.thresholds["low_ctr"]

        low_ctr_df = df[df["ctr"] < threshold][[
            "campaign_name",
            "adset_name",
            "creative_type",
            "creative_message",
            "ctr",
            "impressions",
            "country",
            "audience_type"
        ]]

        return low_ctr_df.to_dict(orient="records")

    def build_summary(self):
        df = self.load_data()

        summary = {
            "dataset_info": {
                "rows": len(df),
                "columns": list(df.columns)
            },
            "daily_summary": self.summarize_daily(df),
            "creative_summary": self.summarize_by_creative(df),
            "audience_summary": self.summarize_by_audience(df),
            "low_ctr_ads": self.get_low_ctr_ads(df)
        }

        return summary
