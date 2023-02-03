
cd web
export JAVA_OPTS="-Dio.swagger.parser.util.RemoteUrl.trustAll=true -Dio.swagger.v3.parser.util.RemoteUrl.trustAll=true"
npm run generate:api
SCRIPT_DIR=$(pwd)


pushd "${SCRIPT_DIR}/src/app/openapi/api"

for file in *;
do
    echo 'fixing' + $file
    sed -i '' 's/localVarHeaders/headers/g' $file;
done
popd
