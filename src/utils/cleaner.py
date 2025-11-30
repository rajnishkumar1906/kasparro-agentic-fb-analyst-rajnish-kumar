import pandas as pd
import numpy as np

class DataCleaner:
    def __init__(self):
        # mapping of broken characters to corrected version
        self.char_map = {
            "â€”": "—",
            "â€“": "–",
            "â€˜": "‘",
            "â€™": "’",
            "â€œ": "“",
            "â€�": "”",
            "â€": "'",
            "â€‹": "",
            "â€¦": "…",
            "â€¢": "•",
            "â€‘": "-",
            "Ã©": "é",
            "Â": ""
        }

    def fix_encoding(self, text):
        if not isinstance(text, str):
            return text
        for bad, good in self.char_map.items():
            text = text.replace(bad, good)
        return text

    def clean_dataframe(self, df: pd.DataFrame):
        df = df.copy()

        # 1️⃣ Fix text encoding in all string columns
        for col in df.select_dtypes(include=["object"]).columns:
            df[col] = df[col].astype(str).apply(self.fix_encoding)

        # 2️⃣ Convert date column
        df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")

        # 3️⃣ Fill missing numeric values
        numeric_cols = ["spend", "impressions", "clicks", "purchases", "revenue", "ctr", "roas"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        # 4️⃣ Recalculate CTR & ROAS
        df["ctr"] = df.apply(
            lambda x: x["clicks"] / x["impressions"] if x["impressions"] > 0 else 0,
            axis=1
        )
        df["roas"] = df.apply(
            lambda x: x["revenue"] / x["spend"] if x["spend"] > 0 else 0,
            axis=1
        )

        return df
