# PowerDominationToolbox

To maintain compatability with SageMath and the Minimum Rank Sage Library, the following code will load this library:

```python
URL = 'https://raw.githubusercontent.com/JibJibFlutterhousen/PowerDominationToolbox/main/PowerDominationToolbox.py'
load(URL)
```

For importing this library from witin CoCalc with a free account you must do the following because CoCalc does not allow an outside internet connection with a free account.

1. Download this code as a zip file.
2. Extract the zip file on your local machine.
3. Go to your project in CoCalc and upload the file "PowerDominationToolbox.py".
4. Execute the following command in your sage worksheet:
```python
load("PowerDominationToolbox.py")
```

The PDT offers functions for:
1. Zero forcing, ```ZeroForce```,
2. Domination, ```Dominate```,
3. Power domination, ```PowerDominate```,
4. Determining if a set is a power dominating set, ```isPDS```,
5. Locating a minimum power dominating set, ```minpds```,
6. Calculating the power domination number of a graph, ```pdn```, and
7. Locating all minimum power dominating sets, ```allminpds```

This project was sponsored, in part, by the Air Force Research Laboratory via the Autonomy Technology Research Center and Wright State University.
This research was also supported by Air Force Office of Scientific Research award 23RYCOR004, and is Distribution A under the reference number APRS-RYA-2023-05-00002.
