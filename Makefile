.PHONY: install data train test api dashboard all

install:
	python -m pip install -r requirements.txt

data:
	python src/clean.py

train:
	python src/train_model.py

test:
	pytest tests/

api:
	python -m uvicorn src.api:app --reload

dashboard:
	python -m streamlit run dashboard/app.py

all: install data train test