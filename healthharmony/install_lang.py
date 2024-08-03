import spacy


def download_models():
    try:
        spacy.cli.download("en_core_web_sm")
        print("Model 'en_core_web_sm' downloaded successfully.")
    except Exception as e:
        print(f"Error downloading model: {e}")


if __name__ == "__main__":
    download_models()
