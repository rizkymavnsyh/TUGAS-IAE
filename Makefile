SHELL := /bin/bash

.DEFAULT_GOAL := help

install:
	pip install -r requirements.txt

lint:
	flake8 .

format:
	black .

test:
	pytest

help:
	@echo "================================================================"
	@echo " Perintah yang Tersedia:"
	@echo "================================================================"
	@echo " make install      -> Menginstal semua dependensi proyek."
	@echo " make lint         -> Memeriksa gaya penulisan kode dengan flake8."
	@echo " make format       -> Merapikan format kode dengan black."
	@echo " make test         -> Menjalankan semua unit test dengan pytest."
	@echo "================================================================"
