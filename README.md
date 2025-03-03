# PowerDominationToolbox

## CoCalc/Sage Integration
To maintain compatability with SageMath and the Minimum Rank Sage Library, the following commands will load this library:

```python
URL = 'https://raw.githubusercontent.com/JibJibFlutterhousen/PowerDominationToolbox/main/src/powerdominationtoolbox/powerdominationtoolbox.py'
load(URL)
```

For importing this library from witin CoCalc with a free account you must do the following because CoCalc does not allow an outside internet connection with a free account.

1. Download this code as a zip file.
2. Extract the zip file on your local machine.
3. Go to your project in CoCalc and upload the file "powerdominationtoolbox.py".
4. Execute the following command in your sage worksheet.
```python
load("powerdominationtoolbox.py")
```

## Using the Power Domination Toolbox
The PDT offers functions for:
1. Zero forcing, ```ZeroForce```,
2. Domination, ```Dominate```,
3. Power domination, ```PowerDominate```,
4. Determining if a set is a power dominating set, ```isPDS```,
5. JL-BW, brute force, method for locating a minimum power dominating set, ```JLBW_minpds```,
6. Brute force, method for locating a minimum power dominating set by way of solving the restricted power domination problem on $G'$ subject to Pref $(G')$, ```PDT_minpds```,
7. Calculating the power domination number of a graph, ```PDT_pdn```, and
8. Locating all power dominating sets of a given size while leveraging parallel computing methods, ```parallel_allpds_of_size```.

## Datasets
The provided graph datasets are encoded in graph6 format.
For information on this graph format, please see http://users.cecs.anu.edu.au/~bdm/data/formats.txt.
Dataset_1.g6 contains 600, connected, Erdos-Renyi random graphs (100 each on 20, 40, 60, 80, 100, and 120 vertices) with edge probability of 0.05.
Dataset_2.g6 contains 665, connected, Erdos-Renyi random graphs on 80 vertices with edge probability of 0.05.

## Funding
This project was sponsored, in part, by the Air Force Research Laboratory via the Autonomy Technology Research Center and Wright State University.
This research was also supported by Air Force Office of Scientific Research award 23RYCOR004, and is Distribution A under the reference number AFRL-2023-2384 and AFRL-2024-1739.
