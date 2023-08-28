
import psycopg2
import psycopg2.extras as extras

def get_secret(secret_name: str, region_name:str) -> str:
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    # In this sample we only handle the specific exceptions for the 'GetSecretValue' API.
    # See https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
    # We rethrow the exception by default.
    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
        response = get_secret_value_response
    except ClientError as e:
        if e.response['Error']['Code'] == 'DecryptionFailureException':
            # Secrets Manager can't decrypt the protected secret text using the provided KMS key.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InternalServiceErrorException':
            # An error occurred on the server side.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidParameterException':
            # You provided an invalid value for a parameter.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'InvalidRequestException':
            # You provided a parameter value that is not valid for the current state of the resource.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        elif e.response['Error']['Code'] == 'ResourceNotFoundException':
            # We can't find the resource that you asked for.
            # Deal with the exception here, and/or rethrow at your discretion.
            raise e
        else:
            # Decrypts secret using the associated KMS key.
            # Depending on whether the secret is a string or binary, one of these fields will be populated.
            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                response = secret
            else:
                decoded_binary_secret = base64.b64decode(get_secret_value_response['SecretBinary'])
                response = decoded_binary_secret
    return response




def execute_values_change_on_primary_k(conn,df,schema_table,

                            primary_k_tuple,lista_conflict =["liquidativo"],
                            close_connection = 'yes' ):
  # excluded lis
  lista_conflict_entera = []
  for i in lista_conflict:
      xx =i +'=' + 'EXCLUDED'+'.'+i
      lista_conflict_entera.append(xx)
  lista_string = (','.join(lista_conflict_entera))


  # Create a list of tupples from the dataframe values
  tuples = [tuple(x) for x in df.to_numpy()]
  # Comma-separated dataframe columns
  cols = ','.join(list(df.columns))
  # SQL quert to execute
  query  = f"INSERT INTO %s(%s) VALUES %%s ON CONFLICT {primary_k_tuple} DO UPDATE SET {lista_string}" % (schema_table, cols)
  cursor = conn.cursor()
  try:
      extras.execute_values(cursor, query, tuples)
      conn.commit()
  except (Exception, psycopg2.DatabaseError) as error:
      print("Error: %s" % error)
      conn.rollback()
      cursor.close()
      return 1
  print("execute_values() done")
  if close_connection == "yes":
      conn.close()
