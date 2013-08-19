#!/bin/bash

jar_folder="/opt/systemsens/service/visualization/jars/"
cur_folder="/opt/systemsens/service/visualization/REU/"
#JAR FILES
weka_path="${jar_folder}weka-mod.jar"
json_path="${jar_folder}json-simple-1.1.1.jar"
msql_path="${jar_folder}mysql-connector-java-5.1.26-bin.jar"

javac -cp $weka_path:$json_path:$msql_path UpdateJSON.java Worker.java
