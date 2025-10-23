import pandas as pd

class IntercropRecommender:
    def __init__(self, csv_path="intercrop_data.csv"):
        """
        Initialize the recommender with a CSV file.
        CSV must have columns:
        main_crop, intercrop1, intercrop2, intercrop3, comment,
        optionA_main, optionA_ic_pct, optionB_main, optionB_ic_pct, optionC_main, optionC_ic_pct, note
        """
        self.data = pd.read_csv(csv_path)
        self.data['main_crop_clean'] = self.data['main_crop'].str.lower().str.strip()

    def list_available_crops(self):
        """Return a list of all available main crops."""
        return self.data['main_crop'].tolist()

    def get_basic_recommendation(self, main_crop):
        """
        Return the basic intercrop recommendation:
        intercrops (1–3) and a brief comment.
        """
        main_crop_clean = main_crop.strip().lower()
        result = self.data[self.data['main_crop_clean'] == main_crop_clean]

        if result.empty:
            return None

        row = result.iloc[0]
        return {
            "Main Crop": row['main_crop'],
            "Intercrops": [row['intercrop1'], row['intercrop2'], row['intercrop3']],
            "Comment": row['comment']
        }

    def get_detailed_recommendation(self, main_crop):
        """
        Return detailed allocation and note information
        for each intercrop option.
        """
        main_crop_clean = main_crop.strip().lower()
        result = self.data[self.data['main_crop_clean'] == main_crop_clean]

        if result.empty:
            return None

        row = result.iloc[0]
        details = {
            "Main Crop": row['main_crop'],
            "Options": {
                "Option A": {
                    "Intercrop": row['intercrop1'],
                    "Main Crop %": row['optionA_main'],
                    "Intercrop %": row['optionA_ic_pct']
                },
                "Option B": {
                    "Intercrop": row['intercrop2'],
                    "Main Crop %": row['optionB_main'],
                    "Intercrop %": row['optionB_ic_pct']
                },
                "Option C": {
                    "Intercrop": row['intercrop3'],
                    "Main Crop %": row['optionC_main'],
                    "Intercrop %": row['optionC_ic_pct']
                }
            },
            "Note": row['note']
        }
        return details
