#!/bin/bash

user_imei=$1
class_path="/opt/systemsens/service/visualization/weka.jar"
folder_path="/opt/systemsens/service/visualization/REU"
model_path="${folder_path}/models/${user_imei}.model"
arff_path="${folder_path}/wekadata/${user_imei}.arff"
modified_path="${folder_path}/wekadata/${user_imei}_modified.arff"
# modify arff_path to match file output.

# JAR FILES

jar_folder="/opt/systemsens/service/visualization/jars/"
weka_path="${jar_folder}weka-mod.jar"
json_path="${jar_folder}json-simple-1.1.1.jar"
msql_path="${jar_folder}mysql-connector-java.5.1.26-bin.jar"
exec_path="${jar_folder}weka-update.jar"

weka_folder_path="${folder_path}/wekadata"

echo neslrocks! | sudo -S chmod 0777 -R $weka_folder_path

#delete command for rows not needed (can be eliminated in ARFF creation itself)
java -cp $class_path weka.filters.unsupervised.attribute.Remove -R 1,3,6,10,12 -i $arff_path -o $modified_path

java -jar $exec_path $user_imei

#run model and dump to model file
#java -cp $class_path weka.classifiers.lazy.IBk -K 1 -W 0 -A "weka.core.neighboursearch.KDTree -A \"weka.core.EuclideanDistance -R first-last\" -S weka.core.neighboursearch.kdtrees.SlidingMidPointOfWidestSide -W 0.01 -L 40 -N" -t $modified_path -d $model_path
#java -cp $class_path weka.classifiers.trees.RandomTree -K 0 -M 1.0 -S 1 -t $modified_path -d $model_path
#java -cp $class_path weka.classifiers.trees.J48 -C 0.25 -M 2 -t $modified_path -d $model_path
#update model in database (not sure why we're doing this anymore because it seems like an unnecessary way to store it)
#mysql -u root -pneslrocks! -e "UPDATE user_models SET model=LOAD_FILE(${model_path}) WHERE imei=${user_imei}" service

# Delete ARFF file from server | commented out for debugging
#rm $arff_path
