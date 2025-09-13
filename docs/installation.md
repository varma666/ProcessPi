---
title: Installation
---

# Installation

ProcessPI is a Python toolkit for **process modeling, simulation, and analysis**.  
It allows engineers to design and simulate pipelines, equipment, and networks with real-world accuracy.  

We **recommend Google Colab** for new users because it provides a **zero-setup environment**, comes pre-installed with common Python packages, and allows you to **run simulations instantly without installing anything locally**.

---

<div class="grid cards" markdown style="grid-template-columns: 1fr; gap: 1.5rem;">

-   :material-cloud-outline: **Google Colab (Recommended)**  
    Google Colab provides a cloud-based Python environment. You can try ProcessPI without worrying about local installations or dependencies.  
    **Install and import in Colab**:
    ```python
    !pip install processpi
    from processpi.components import Water
    print(Water().density())
    ```
    Recommended for beginners, testing examples, and sharing notebooks easily.

-   :material-download: **Install from PyPI**  
    Quickest method for installing ProcessPI in your local Python environment. Works for most users:
    ```bash
    pip install processpi
    ```
    Best for running scripts locally without cloning the source.

-   :material-hammer-wrench: **Development Setup**  
    If you want to contribute or customize ProcessPI, clone the repository and install in editable mode:
    ```bash
    git clone https://github.com/varma666/ProcessPi.git
    cd ProcessPi
    pip install -e .
    ```
    Allows live editing of code and testing changes immediately.

-   :material-shield: **Using a Virtual Environment (Recommended for Local Setup)**  
    Protect your system Python and avoid dependency conflicts:
    ```bash
    python -m venv .venv
    # Linux / macOS
    source .venv/bin/activate
    # Windows
    .venv\Scripts\activate
    pip install processpi
    ```
    Recommended for stable development and isolating projects.

-   :material-notebook-outline: **Using in Jupyter Notebook**  
    Jupyter Notebook allows interactive simulations. Install Jupyter if not available:
    ```bash
    pip install jupyter
    jupyter notebook
    ```
    Then import ProcessPI:
    ```python
    from processpi.units import Length, Pressure
    print(Length(1, "m").to("ft"))
    ```
    Ideal for step-by-step examples, tutorials, and exploring features.

-   :material-check-circle-outline: **Verification**  
    Ensure ProcessPI is installed correctly:
    ```python
    import processpi
    print("ProcessPI version:", processpi.__version__)
    ```
    Confirms your environment is ready to run simulations.

</div>
