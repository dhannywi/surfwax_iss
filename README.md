# Surf Wax ISS
Surf Wax ISS is a containarized Flask application for querying and returning interesting information from the ISS positional and velocity data. You can find version 1.0 of the App [here](https://github.com/dhannywi/COE332/tree/main/homework04). In [version 2.0](https://github.com/dhannywi/COE332/tree/main/homework05), we improved the App to make the REST API more useful and  *portable*, and added even more functionality for the latest release.

More information about the dataset used can be found in the [ISS Trajectory Data](https://spotthestation.nasa.gov/trajectory_data.cfm) website. The Orbital Ephemeris Message (OEM) data used contains ISS state vectors over a ~15 day period.

## Implementation
The project uses **Python 3.8.10**, in particular **Flask 2.2.2**, and **Docker 20.10.12** for containerization. 

Specific Python3 libraries are used:
* `math`
* `flask`
* `requests`
* `xmltodict`

### Files
* `Dockerfile` -- commands for building a new image
* `docker-compose.yml` -- multi-container applications management
* `iss_tracker.py` -- python scripts for the Flask application
* `README.md` -- project documentation

## Installation

You have the option to build this project from source, or use the provided Docker container on DockerHub. A Docker installation is required, as we build and run a Docker image.

We describe below the installation process using terminal commands, which are expected to run on a Ubuntu 20.04.5 machine with Python3. Installation may differ for other systems.

<details>
<summary><b>From Docker (option 1)</b></summary>

**Install**

* To install the Docker container, first install Docker: `apt-get install docker` or follow installation instructions for [Docker Desktop](https://www.docker.com/get-started/) for your system. We are using Docker 20.10.12

* Next, pull the image from the docker hub and install the containers: `docker pull dhannywi/iss_tracker:2.0`

* Check the docker images currently running in your computer by executing: `docker images`
The image you just installed would show up in the list of images:
```console
username:~/COE332/homework05$ docker images
REPOSITORY             TAG       IMAGE ID       CREATED         SIZE
username/iss_tracker   2.0       fc2baf131ff1   4 minutes ago   897MB
```

**Run**

* To run the code, execute: `docker run -it --rm -p 5000:5000 dhannywi/iss_tracker:2.0` 
The terminal should return a link, which can be viewed via a browser or with the curl commands documented in the API reference section. Your local server is up and running when you see this message:
```console
username:~/COE332/homework05$ docker run -it --rm -p 5000:5000 dhannywi/iss_tracker:2.0
 * Serving Flask app 'iss_tracker'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://129.114.39.216:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 634-065-858
```

</details>


<details>
<summary><b>Source build (option 2)</b></summary>

Since this is a Docker build, the requirements need not be installed, as it will automatically be done on the Docker image. All commands, unless otherwise noted, are to be run in a terminal (in the `homework05` directory of the cloned repository).

**Build**

* First, install Docker: `apt-get install docker` or follow installation instructions for [Docker Desktop](https://www.docker.com/get-started/) for your system. We are using Docker 20.10.12
* Next, clone the  repository: `git clone https://github.com/dhannywi/COE332.git`
* Then, change directory into the `homework05` folder: `cd .\COE332\homework05\`
* Now, build the image: `docker build -t dhannywi/iss_tracker:2.0 .`
This output shows that your build is successful:
```console
username:~/COE332/homework05$ docker build -t dhannywi/iss_tracker:2.0 .
Sending build context to Docker daemon  61.44kB
...
...
...
Successfully built fc2baf131ff1
Successfully tagged dhannywi/iss_tracker:2.0
```
* Check the docker images currently running in your computer by executing: `docker images`
The image you just built would show up in the list of images:
```console
username:~/COE332/homework05$ docker images
REPOSITORY             TAG       IMAGE ID       CREATED         SIZE
username/iss_tracker   2.0       fc2baf131ff1   4 minutes ago   897MB
```

**Run**

* To run the code, please execute: `docker run -it --rm -p 5000:5000 dhannywi/iss_tracker:2.0` 
The terminal should return a link, which can be viewed via a browser or with the curl commands documented in the API reference section. Your local server is up and running when you see this message:
```console
username:~/COE332/homework05$ docker run -it --rm -p 5000:5000 dhannywi/iss_tracker:2.0
 * Serving Flask app 'iss_tracker'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://129.114.39.216:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 634-065-858
```

</details>
<br>

## Usage
Once you have the docker image running with dependencies installed and the local server running, we can start querying using the REST API in the Flask app.

There are thirteen routes for you to request data from:

|    | Route | Method | What it returns |
| -- | ----- | ------ | --------------------- |
| 1. | `/`   | GET | The entire data set   |
| 2. | `/epochs` | GET | A list of all Epochs in the data set |
| 3. | `/epochs?limit=int&offset=int` | GET | Return modified list of Epochs given query parameters |
| 4. | `/epochs/<epoch>` | GET | State vectors for a specific Epoch from the data set |
| 5. | `/epochs/<epoch>/speed` | GET | Instantaneous speed for a specific Epoch in the data set |
| 6. | `/help` | GET | Return help text (as a string) that briefly describes each route |
| 7. | `/delete-data` | DELETE | Delete all data from the dictionary object |
| 8. | `/post-data` | POST | Reload the dictionary object with data from the web |
| 9. | `/comment` |GET | Return ‘comment’ list object from ISS data |
| 10. | `/header` | GET | Return ‘header’ dict object from ISS data |
| 11. | `/metadata` | GET | Return ‘metadata’ dict object from ISS data |
| 12. | `/epochs/<epoch>/location` | GET | Return latitude, longitude, altitude, and geoposition for given Epoch |
| 13. | `/now` | GET | Return latitude, longitude, altidue, and geoposition for Epoch that is nearest in time |


### Querying ISS data using the REST API
Since we need to keep the server running in order to make requests, open an additional shell and change your directory to the same directory your server is running. Keep in mind that in order to query specific data, you will need to query `/` or `/post-data` routes first in order to load (or re-load) dataset into the App. Otherwise, when data has not been loaded/ has been deleted, you will receive an error message. For example:
```console
username:~/COE332/homework05$ curl localhost:5000/epochs/2023-061T08:09:00.000Z/speed
No data found. Please reload data.
```

#### 1. Route `/`

Now we will make a request to the Flask app by executing the command `curl localhost:5000` on your terminal. The output should be similar to below:

```console
username:~/COE332/homework05$ curl localhost:5000/
{ .....
              {
                "EPOCH": "2023-061T12:00:00.000Z",
                "X": {
                  "#text": "3578.8574821437401",
                  "@units": "km"
                },
                "X_DOT": {
                  "#text": "5.03904352218286",
                  "@units": "km/s"
                },
                "Y": {
                  "#text": "-5454.7252313410299",
                  "@units": "km"
                },
                "Y_DOT": {
                  "#text": "1.32725609415084",
                  "@units": "km/s"
                },
                "Z": {
                  "#text": "1908.4598652639199",
                  "@units": "km"
                },
                "Z_DOT": {
                  "#text": "-5.6136727354188301",
                  "@units": "km/s"
                }
              }
            ]
          },
          "metadata": {
            "CENTER_NAME": "EARTH",
            "OBJECT_ID": "1998-067-A",
            "OBJECT_NAME": "ISS",
            "REF_FRAME": "EME2000",
            "START_TIME": "2023-046T12:00:00.000Z",
            "STOP_TIME": "2023-061T12:00:00.000Z",
            "TIME_SYSTEM": "UTC"
          }
        }
      },
      "header": {
        "CREATION_DATE": "2023-047T00:51:05.746Z",
        "ORIGINATOR": "JSC"
      }
    }
  }
}
```

#### 2. Route `/epochs`
Next, we will query for a list of all Epochs in the data set. Execute the command `curl localhost:5000/epochs` on your terminal. You should get output similar to this:

```console
username:~/COE332/homework05$ curl localhost:5000/epochs
[ ....,
  "2023-061T11:35:00.000Z",
  "2023-061T11:39:00.000Z",
  "2023-061T11:43:00.000Z",
  "2023-061T11:47:00.000Z",
  "2023-061T11:51:00.000Z",
  "2023-061T11:55:00.000Z",
  "2023-061T11:59:00.000Z",
  "2023-061T12:00:00.000Z",
  ....
]
```

#### 3. Route `/epochs?limit=int&offset=int`
As the output from the previous query can be lengthy, we have added an option to limit the amout of data presented to the user. Execute the command `curl "localhost:5000/epochs?limit=int&offset=int"` to query a modified list of Epochs based on a given query parameters.

**Note:** you need to use double quotation ("") around the URL request for the query to work.

The `offset` query parameter should offset the start point by an integer. For example, `offset=0` would begin printing at the first Epoch, `offset=1` would begin printing at the second Epoch, etc. The `limit` query parameter controls how many results are returned. For example `limit=10` would return 10 Epochs, `limit=100` would return 100 Epochs, etc.

As an example, when you execute the command `curl "localhost:5000/epochs?limit=20&offset=50"`, the program would return Epochs 51 through 70 (20 total):
```console
username:~/COE332/homework05$ curl "localhost:5000/epochs?limit=20&offset=50"
[
  "2023-058T15:20:00.000Z",
  "2023-058T15:24:00.000Z",
  "2023-058T15:28:00.000Z",
  "2023-058T15:32:00.000Z",
  "2023-058T15:36:00.000Z",
  "2023-058T15:40:00.000Z",
  "2023-058T15:44:00.000Z",
  "2023-058T15:48:00.000Z",
  "2023-058T15:52:00.000Z",
  "2023-058T15:56:00.000Z",
  "2023-058T16:00:00.000Z",
  "2023-058T16:04:00.000Z",
  "2023-058T16:08:00.000Z",
  "2023-058T16:12:00.000Z",
  "2023-058T16:16:00.000Z",
  "2023-058T16:20:00.000Z",
  "2023-058T16:24:00.000Z",
  "2023-058T16:28:00.000Z",
  "2023-058T16:32:00.000Z",
  "2023-058T16:36:00.000Z"
]
```

However, if your input is invalid, you will get an error message. Below are some examples of error messages you can expect:
```console
username:~/COE332/homework05$ curl "localhost:5000/epochs?limit=20&offset=y"
Bad Request. Invalid offset parameter.
```

```console
username::~/COE332/homework05$ curl 'localhost:5000/epochs?limit=a&offset=10'
Bad Request. Invalid limit parameter.
```

```console
username:~/COE332/homework05$ curl "localhost:5000/epochs?limit=-20&offset=-10"
Bad Request. `offset` or `limit` parameter is either too large or too small.
```

#### 4. Route `/epochs/<epoch>`
Since we now know the epochs in the data set, we can query for the state vectors for a specific Epoch. To do this, Execute the command `curl localhost:5000/epochs/<epoch>` on your terminal, but replace `<epoch>` with a particular epoch you are interested in.
For example: `curl localhost:5000/epochs/2023-061T08:09:00.000Z`

The resulting output will be similar to below:

```console
username:~/COE332/homework05$ curl localhost:5000/epochs/2023-061T08:09:00.000Z
{
  "EPOCH": "2023-061T08:09:00.000Z",
  "X": {
    "#text": "-3961.79394994832",
    "@units": "km"
  },
  "X_DOT": {
    "#text": "-4.7028919269355596",
    "@units": "km/s"
  },
  "Y": {
    "#text": "5298.7862135964297",
    "@units": "km"
  },
  "Y_DOT": {
    "#text": "-1.8472846937741301",
    "@units": "km/s"
  },..
  "Z": {
    "#text": "-1545.43747234906",
    "@units": "km"
  },
  "Z_DOT": {
    "#text": "5.7616942719771602",
    "@units": "km/s"
  }
}
```

However, if you request an invalid epoch, for example `curl localhost:5000/epochs/xyz`, you will get:
```console
username:~/COE332/homework05$ curl localhost:5000/epochs/xyz
The epoch you requested is not in the data.
```

#### 5. Route `/epochs/<epoch>/speed`
We can also query for the instantaneous speed for a specific Epoch in the data set by executing the command `curl localhost:5000/epochs/<epoch>/speed` on your terminal, but replace `<epoch>` with a particular epoch you are interested in.
For example: `curl localhost:5000/epochs/2023-061T08:09:00.000Z/speed`

It will output the resulting speed calculation as below:

```console
username:~/COE332/homework05$ curl localhost:5000/epochs/2023-061T08:09:00.000Z/speed
The instantaneous speed for the epoch you requested is 7.6633 km/s.
```

However, if you request an invalid epoch, for example `curl localhost:5000/epochs/xyz/speed`, you will get:
```console
username:~/COE332/homework05$ curl localhost:5000/epochs/xyz/speed
We are unable to calculate speed. Invalid Epoch.
```

#### 6. Route `/help`

Execute the command `curl localhost:5000/help` to get a brief description each route. The output will be similar to below:

```console
username:~/COE332/homework04$ curl localhost:5000/help
    Usage: curl localhost:5000[ROUTE]

    A Flask application for querying and returning interesting information from the ISS data set.

    Route                           Method  What it returns
    /                               GET     Return entire data set
    /epochs                         GET     Return list of all Epochs in the data set
    /epochs?limit=int&offset=int    GET     Return modified list of Epochs given query parameters
    /epochs/<epoch>                 GET     Return state vectors for a specific Epoch from the data set
    /epochs/<epoch>/speed           GET     Return instantaneous speed for a specific Epoch in the data set
    /help                           GET     Return help text that briefly describes each route
    /delete-data                    DELETE  Delete all data from the dictionary object
    /post-data                      POST    Reload the dictionary object with data from the web
    /comment                        GET     Return ‘comment’ list object from ISS data
    /header                         GET     Return ‘header’ dict object from ISS data
    /metadata                       GET     Return ‘metadata’ dict object from ISS data
    /epochs/<epoch>/location        GET     Return latitude, longitude, altitude, and geoposition for given Epoch
```

#### 7. Route `/delete-data`

To delete data, execute the command `curl localhost:5000/delete-data -X DELETE`. Data deletion is confirmed when you receive the output:

```console
username:~/COE332/homework04$ curl localhost:5000/delete-data -X DELETE
All data has been removed.
```

However, if you run the curl command without loading the data first, you will get an erroe message:
```console
username:~/COE332/homework05$ curl localhost:5000/delete-data -X DELETE
No data to delete.
```

#### 8. Route `/post-data`

To populate or update the ISS data, run the command `curl localhost:5000/post-data -X POST`. A successful session results in a similar output:

```console
username:~/COE332/homework04$ curl localhost:5000/post-data -X POST
{.....
              {
                "EPOCH": "2023-073T12:00:00.000Z",
                "X": {
                  "#text": "-1245.0878940228999",
                  "@units": "km"
                },
                "X_DOT": {
                  "#text": "4.7140040881658498",
                  "@units": "km/s"
                },
                "Y": {
                  "#text": "-6674.6926971496696",
                  "@units": "km"
                },
                "Y_DOT": {
                  "#text": "-0.60161940965214999",
                  "@units": "km/s"
                },
                "Z": {
                  "#text": "-319.31248886637098",
                  "@units": "km"
                },
                "Z_DOT": {
                  "#text": "-6.0082507229750703",
                  "@units": "km/s"
                }
              }
            ]
          },
          "metadata": {
            "CENTER_NAME": "EARTH",
            "OBJECT_ID": "1998-067-A",
            "OBJECT_NAME": "ISS",
            "REF_FRAME": "EME2000",
            "START_TIME": "2023-058T12:00:00.000Z",
            "STOP_TIME": "2023-073T12:00:00.000Z",
            "TIME_SYSTEM": "UTC"
          }
        }
      },
      "header": {
        "CREATION_DATE": "2023-058T21:02:19.972Z",
        "ORIGINATOR": "JSC"
      }
    }
  }
}
```

#### 9. Route `/comment`
Execute the command `curl localhost:5000/comment` on your terminal, and you will get the "comment" information from ISS data.
```console
username:~/surfwax_iss$ curl localhost:5000/comment
[
  "Units are in kg and m^2",
  "MASS=461235.00",
  "DRAG_AREA=1964.62",
  "DRAG_COEFF=2.50",
  "SOLAR_RAD_AREA=0.00",
  "SOLAR_RAD_COEFF=0.00",
  "Orbits start at the ascending node epoch",
  "ISS first asc. node: EPOCH = 2023-03-01T12:07:31.114 $ ORBIT = 2508 $ LAN(DEG) = 161.00612",
  "ISS last asc. node : EPOCH = 2023-03-16T11:13:47.515 $ ORBIT = 2740 $ LAN(DEG) = 85.61938",
  "Begin sequence of events",
  "TRAJECTORY EVENT SUMMARY:",
  null,
  "|       EVENT        |       TIG        | ORB |   DV    |   HA    |   HP    |",
  "|                    |       GMT        |     |   M/S   |   KM    |   KM    |",
  "|                    |                  |     |  (F/S)  |  (NM)   |  (NM)   |",
  "=============================================================================",
  "Crew06 Launch         061:05:34:13.000             0.0     427.0     408.8",
  "(0.0)   (230.6)   (220.7)",
  null,
  "Crew06 Docking        062:06:11:00.000             0.0     426.9     408.4",
  "(0.0)   (230.5)   (220.5)",
  null,
  "GMT 067 ISS Reboost   067:20:02:00.000             0.9     427.0     407.3",
  "(3.0)   (230.6)   (219.9)",
  null,
  "Crew05 Undock         068:08:00:00.000             0.0     427.0     410.4",
  "(0.0)   (230.6)   (221.6)",
  null,
  "SpX27 Launch          074:00:30:00.000             0.0     426.7     409.5",
  "(0.0)   (230.4)   (221.1)",
  null,
  "SpX27 Docking         075:12:00:00.000             0.0     426.7     409.4",
  "(0.0)   (230.4)   (221.1)",
  null,
  "=============================================================================",
  "End sequence of events"
]i
```

#### 10. Route `/header`
To get the header information from ISS data, execute `curl localhost:5000/header` on your terminal.
```console
username:~/surfwax_iss$ curl localhost:5000/header
{
  "CREATION_DATE": "2023-060T20:39:58.746Z",
  "ORIGINATOR": "JSC"
}
```

#### 11. Route `/metadata`
Executing the command `curl localhost:5000/metadata` on your terminal will output the ISS metadata information.
```console
username:~/surfwax_iss$ curl localhost:5000/metadata
{
  "CENTER_NAME": "EARTH",
  "OBJECT_ID": "1998-067-A",
  "OBJECT_NAME": "ISS",
  "REF_FRAME": "EME2000",
  "START_TIME": "2023-060T12:00:00.000Z",
  "STOP_TIME": "2023-075T12:00:00.000Z",
  "TIME_SYSTEM": "UTC"
}
```

#### 12. Route `/epochs/<epoch>/location`
Query the ISS location for a specific Epoch by executing the command `curl localhost:5000/epochs/<epoch>/location` on your terminal, but replace <epoch> with a particular epoch you are interested in.
For example, `curl localhost:5000/epochs/2023-061T08:09:00.000Z/location` will output:
```console

```

#### 13. Route `/now`
If you are interested in finding out the current location of ISS, you can execute the command `curl localhost:5000/now`. It will output latitude, longitude, altidue, and geoposition for Epoch that is nearest to the currrent time:
```console

```

## Additional Resources

* [NASA Data Set](https://spotthestation.nasa.gov/trajectory_data.cfm)

## Authors

Dhanny W Indrakusuma<br>
dhannywi@utexas.edu
