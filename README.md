# liquor_sales_iowa

Steps to install and run the app

1. pip install -r requirements.txt
2. If the above gives any errors, and does not install all the packages, please execute the following:

    Create a conda virtual environment (python 3.8) and clone the repo into it

    conda install -c conda-forge pandas
    conda install -c conda-forge plotly
    conda install -c conda-forge dash
    conda install -c conda-forge dash-bootstrap-components
    python -m pip install dash-bootstrap-templates (access pip from the conda virtual environment - For Windows - C:\ProgramData\Anaconda3\envs\<virtual environment name>\python.exe -m pip install dash-bootstrap-templates)
    conda install -c conda-forge dash-extensions
    conda install -c conda-forge dash-bio
    conda install -c conda-forge pystan
    conda install -c conda-forge fbprophet
    conda install -c conda-forge scipy --all

Run app.py
