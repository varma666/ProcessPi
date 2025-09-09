# Installation

ProcessPI can be installed from PyPI, set up in a development environment, or used directly in **Jupyter Notebooks** and **Google Colab**.

---

## 📦 Install from PyPI

The simplest way to install ProcessPI:

```bash
pip install processpi
```
---

## 🛠 Development Setup

If you want to work on the source code:

```bash
git clone https://github.com/varma666/ProcessPi.git
cd ProcessPi
pip install -e .
```
---
## 🐍 Using a Virtual Environment (Recommended)

To avoid conflicts with other Python packages, use a virtual environment.

Create and activate with venv:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux / macOS
.venv\Scripts\activate      # Windows
```
Install ProcessPI inside it:

```bash
pip install processpi
```
---
## 📓 Using in Jupyter Notebook

ProcessPI works inside Jupyter Notebooks.
First, install Jupyter:

```bash
pip install jupyter
```
Launch

```bash
jupyter notebook
```
Inside a notebook, you can import ProcessPI:

```bash
from processpi.units import Length, Pressure
print(Length(1, "m").to("ft"))
```
---

## 🌐 Using in Google Colab

You can use ProcessPI directly in Colab notebooks.

At the top of your Colab notebook, run:

```bash
!pip install processpi
```

Then import as usual:
```bash
from processpi.components import Water
print(Water().density())
```
---
## ✅ Verification

After installation, verify ProcessPI is available:
```bash
import processpi
print("ProcessPI version:", processpi.__version__)
```
