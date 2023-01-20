#!/usr/bin/env python
# coding: utf-8

# In[41]:

# Necessary imports
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# In[42]:


dataset = pd.read_csv('world_bank_data.csv')

cluster_indi_codes = ["IQ.CPA.PUBS.XQ", "AG.LND.ARBL.ZS"]
cluster_years = ["2005", "2020"]


def data_frame_extracted(cluster_indi_codes, cluster_years):
    """ This function takes two arguments, `cluster_indi_codes` and `cluster_years`, and extracts the data from the dataset for a given Indicator Code and given year. It then drops some columns from the dataset to create a new dataframe and returns a list of dataframes. 
"""
    public_sector = dataset[dataset["Indicator Code"] == cluster_indi_codes[0]]
    arable_land = dataset[dataset["Indicator Code"] == cluster_indi_codes[1]]
    # fodata
    public_sector = public_sector.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")
    arable_land = arable_land.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")
    dfs = []
    for year in cluster_years:
        public_ = public_sector[year]
        arable_ = arable_land[year]
        data_frame = pd.DataFrame(
            {"CPIA public sector management ": public_, "Arable land": arable_})
        df = data_frame.dropna(axis=0)
        dfs.append(df)

    return dfs


dfs_cluster = data_frame_extracted(cluster_indi_codes, cluster_years)


# In[43]:

# In[48]:


def clustering(data_frames):
    """
This function clusters a list of dataframes using k-means algorithm. The function first scales the data using standard scaling technique and then finds the optimum number of clusters using the elbow method. It then fits the k-means algorithm to the dataset and plots the clusters and their centroids on the original data. 
"""
    year = "2005"
    for df in data_frames:
        x = df.values
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        # Finding the optimum number of clusters
        wcss = []
        for i in range(1, 11):
            kmeans = KMeans(n_clusters=i, init='k-means++',
                            max_iter=300, n_init=10, random_state=42)
            kmeans.fit(x_scaled)
            wcss.append(kmeans.inertia_)

        # Plotting the elbow graph
        plt.plot(range(1, 11), wcss)
        plt.title('The Elbow Method')
        plt.xlabel('Number of clusters')
        plt.ylabel('WCSS')
        plt.show()

        # Fitting kmeans to the dataset
        kmeans = KMeans(n_clusters=4, init='k-means++',
                        max_iter=300, n_init=10, random_state=0)
        y_kmeans = kmeans.fit_predict(x_scaled)

        # Plotting the clusters on original data
        plt.scatter(x_scaled[y_kmeans == 0, 0], x_scaled[y_kmeans ==
                    0, 1], s=50, c='red', label='Cluster 1')
        plt.scatter(x_scaled[y_kmeans == 1, 0], x_scaled[y_kmeans ==
                    1, 1], s=50, c='blue', label='Cluster 2')
        plt.scatter(x_scaled[y_kmeans == 2, 0], x_scaled[y_kmeans ==
                    2, 1], s=50, c='green', label='Cluster 3')
        plt.scatter(x_scaled[y_kmeans == 3, 0], x_scaled[y_kmeans ==
                    3, 1], s=50, c='cyan', label="Cluster 4")

        # Plotting the centroids
        plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[
                    :, 1], s=100, marker="*", c='black', label='Centroids')

        plt.title(f'Clusters of countries ' + year)
        plt.xlabel("CIPA public sector management")
        plt.ylabel("Arable land")

        plt.legend()
        plt.show()
        year = "2020"


clustering(dfs_cluster)


# In[52]:


def fitting_predictions():
    '''
This function takes in a dataset and performs curve fitting and linear regression to predict CO2 emissions from liquid fuel consumption (kt) based on Urban population growth in selected countries. It also generates a plot to show the best fitting function, confidence range, and plots to show the predicted values in 10 and 20 years. 
'''
    popdata_fit = dataset[dataset["Indicator Code"] == "SP.URB.GROW"]
    fodata_fit = dataset[dataset["Indicator Code"] == "EN.ATM.CO2E.LF.KT"]
    # fodata
    popdata_fit = popdata_fit.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")
    fodata_fit = fodata_fit.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")

    two_pop_fit = popdata_fit["2012"]
    two_fo_fit = fodata_fit["2012"]

    data_frame_fit = pd.DataFrame({
        "Urban_pop_grow": two_pop_fit,
        "co2_con_liq": two_fo_fit})
    data_frame_fit = data_frame_fit.dropna(axis=0)
    data_frame_fit = data_frame_fit.loc[["India", "Australia", "United Kingdom", "Pakistan", "Brazil",
                                         "Canada", "Russian Federation", "South Africa", "Austria", "Portugal", "Argentina", "Bangladesh",]]
    xdata = data_frame_fit.iloc[:, 0].values
    ydata = data_frame_fit.iloc[:, 1].values

    # Define the function to fit
    def func(x, a, b):
        return a*x + b

    # Fit the data
    popt, pcov = curve_fit(func, xdata, ydata)

    # Generate a plot showing the best fitting function
    plt.plot(xdata, ydata, 'o', label='data')
    plt.plot(xdata, func(xdata, *popt), 'r-',
             label='fit: a=%5.3f, b=%5.3f' % tuple(popt))
    plt.title("CO2 emission from liquid fuels vs Urban Population growth")
    plt.xlabel('Urban population growth (annual %)')
    plt.ylabel('CO2 emissions from liquid fuel consumption (kt)')
    plt.legend()
    plt.show()

    # Compute the confidence ranges
    def err_ranges(popt, pcov):
        perr = np.sqrt(np.diag(pcov))
        lower = popt - perr
        upper = popt + perr
        return lower, upper

    # Generate a plot showing the confidence range
    lower, upper = err_ranges(popt, pcov)
    plt.plot(xdata, ydata, 'o', label='data')
    plt.plot(xdata, func(xdata, *popt), 'r-',
             label='fit: a=%5.3f, b=%5.3f' % tuple(popt))
    plt.plot(xdata, func(xdata, *lower), 'b--',
             label='lower: a=%5.3f, b=%5.3f' % tuple(lower))
    plt.plot(xdata, func(xdata, *upper), 'g--',
             label='upper: a=%5.3f, b=%5.3f' % tuple(upper))
    plt.title("CO2 emission from liquid fuels vs Urban Population growth")
    plt.xlabel('Urban population growth (annual %)')
    plt.ylabel('CO2 emissions from liquid fuel consumption (kt)')
    plt.legend()
    plt.bbox_to_anchor = (0.5, -0.5)
    plt.show()

    # Use the model for predictions
    slope, intercept, r_value, p_value, std_err = linregress(xdata, ydata)

    # Predict the values in 10 years
    xpred = 10
    ypred = slope * xpred + intercept
    print("CO2 emissions from liquid fuel consumption (kt) in 10 years: ", ypred)

    # Predict the values in 20 years
    xpred = 20
    ypred = slope * xpred + intercept
    print("CO2 emissions from liquid fuel consumption (kt) in 20 years: ", ypred)


fitting_predictions()
