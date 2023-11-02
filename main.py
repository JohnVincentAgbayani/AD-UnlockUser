import boto3
import time
import os

ssm_file = open("unlock_ad_ssm.json")
ssm_json = ssm_file.read()

env_file = open("temp_env.txt")
target_environment = env_file.read()
target_environment = target_environment.replace("\n","")

user_file = open("temp_user.txt")
target_username = user_file.read()
target_username = target_username.replace("\n","")

instance_ids = {
	"Deltekdev":"i-04d0e953afe07b3a3",
	"DCO":"i-0fe3ff3ff41c18b17",
	"Costpoint":"i-0e82a12d1ef934425",
	"Flexplus":"i-0f2717bceb18eea6f",
	"GlobalOSS":"i-04b225ae477c52288",
	"Engdeltek":"i-0667aa10a44eafc7c",
}

target_instance_id = instance_ids[target_environment]

ssm_doc_name = 'ad-unlock-user'
ssm_client = boto3.client('ssm', region_name="us-east-1")

ssm_create_response = ssm_client.create_document(Content = ssm_json, Name = ssm_doc_name, DocumentType = 'Command', DocumentFormat = 'JSON', TargetType =  "/AWS::EC2::Instance")

ssm_run_response = ssm_client.send_command(InstanceIds = [target_instance_id], DocumentName=ssm_doc_name, DocumentVersion="$DEFAULT", TimeoutSeconds=120,  Parameters={'Username':[target_username]})
print(f'{ssm_run_response}\n')
cmd_id = ssm_run_response['Command']['CommandId']

time.sleep(5)
ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_instance_id)
while ssm_status_response['StatusDetails'] == 'InProgress':
	time.sleep(5)
	ssm_status_response = ssm_client.get_command_invocation(CommandId=cmd_id, InstanceId=target_instance_id)

if ssm_status_response['StatusDetails'] == 'Success':
	print(f'User {target_username} has been unlocked in {target_environment}\n')

ssm_delete_response = ssm_client.delete_document(Name=ssm_doc_name)