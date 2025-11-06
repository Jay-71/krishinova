import pandas as pd

def get_all_schemes(csv_path="scheme.csv"):
    """
    Reads the agriculture schemes CSV file and returns structured data.

    Args:
        csv_path (str): Path to the CSV file (default = 'scheme.csv')

    Returns:
        dict: {"total_schemes": int, "schemes": [ ... list of scheme dicts ... ]}
    """
    try:
        # Load dataset
        df = pd.read_csv(csv_path)

        # Validate required columns
        required_cols = [
            "scheme_name",
            "highlight",
            "detailed_overview",
            "benefits",
            "eligibility",
            "required_documents",
            "source_link"
        ]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            return {"error": f"Missing columns in CSV: {', '.join(missing_cols)}"}

        # Convert to list of dictionaries
        scheme_list = df.to_dict(orient="records")

        return {
            "total_schemes": len(scheme_list),
            "schemes": scheme_list
        }

    except FileNotFoundError:
        return {"error": f"File '{csv_path}' not found."}
    except pd.errors.EmptyDataError:
        return {"error": "CSV file is empty or corrupted."}
    except Exception as e:
        return {"error": str(e)}


# Optional test for standalone use
if __name__ == "__main__":
    from pprint import pprint
    pprint(get_all_schemes("scheme.csv"))
