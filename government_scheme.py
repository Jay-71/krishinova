import pandas as pd

def display_schemes(csv_path):
    try:
        # Load dataset
        df = pd.read_csv(csv_path)

        print("\n✅ Maharashtra Agriculture Schemes Dataset Loaded Successfully!")
        print(f"Total Schemes Found: {len(df)}\n")

        # Display list of schemes with highlights
        for i, row in df.iterrows():
            print(f"🔹 {i+1}. {row['scheme_name']}")
            print(f"   💡 Highlight: {row['highlight']}\n")

        # Allow user to view scheme details
        while True:
            choice = input("Enter scheme number to view details (0 to exit): ")

            if choice == '0':
                print("\n👋 Exiting. Thank you!")
                break

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(df):
                    scheme = df.iloc[idx]
                    print("\n" + "="*50)
                    print(f"📘 Scheme Name: {scheme['scheme_name']}")
                    print(f"💡 Highlight: {scheme['highlight']}")
                    print(f"📝 Detailed Overview: {scheme['detailed_overview']}")
                    print(f"🎁 Benefits: {scheme['benefits']}")
                    print(f"👨‍🌾 Eligibility: {scheme['eligibility']}")
                    print(f"📄 Required Documents: {scheme['required_documents']}")
                    print(f"🔗 Source Link: {scheme['source_link']}")
                    print("="*50 + "\n")
                else:
                    print("⚠️ Invalid number! Try again.")
            except ValueError:
                print("⚠️ Please enter a valid number.")

    except FileNotFoundError:
        print(f"❌ Error: File '{csv_path}' not found.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


# Example usage
if __name__ == "__main__":
    display_schemes("krishinova\scheme.csv")
