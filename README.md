# Pyside6_demo v0.1.1 (change to PyQt5)
Calling API to show Line Chart. 

Launch the API program in your terminal,  After launching, execute the program by pressing the 'Load Data' button.  

Below are introduction to the API's functionality


## Base URL
`http://{host}[:{port}]/api/{version}`
## `tags` resource
Well-known tags CURD.

Path: `/api/{version}/tags[/{register}]`

## GET `{base URL}/tags`
Get tags definiation.

Data schema:
```json

{
    "{register}": {
        "name": "user defined name"
    },
    ...
}

```
GET `{base URL}/{register}`
Get specific tag definiation.

Data schema:
```josn

{
    "name": "user defined name"
}

```
## `detections` resource
Register values detection configuration.

Path: `{base URL}/detection[/{register}]`

## GET `{base URL}/detections`
Get detections definiation.

Data schema:
```json

{
    "{register}": {
        "{detection name}": 
        {
            "condition": "above|below",
            "threshold": <numerical>
        },
        ...
    }
}

```
## GET `{base URL}/detections/{register}`
Get specific detection(s) of register definiation.

Data schema:
```json

{
    "{detection name}": 
    {
        "condition": "above|below",
        "threshold": <numerical>
    },
    ...
}

```
## `collecteds` resource
Collected PLC register data. X (timeslot) and Y (values) lists of data are provided for the creation of a line chart.

Path: `{base URL}/collecteds[/{register}]`

## GET `{base URL}/collecteds`
Get collecteds.

Parameters:

(optional) start – format: yyyy/mm/dd HH:MM:SS
(optional) end – format: yyyy/mm/dd HH:MM:SS
Data schema:

{
    "{register}": {
        "x_axis_labels": ['texts for X axis', ...],
        "y_axis_values": ['values for Y axis', ...]
    },
    ...
}
GET {base URL}/collecteds/{register}
Get specific collecteds of tag.

Parameters:

*(optional) `start` – format: `yyyy/mm/dd HH:MM:SS`
*(optional) `end` – format: `yyyy/mm/dd HH:MM:SS`
Data schema:
```json

{
    "x_axis_labels": ['texts for X axis', ...],
    "y_axis_values": ['values for Y axis', ...]
}

```
