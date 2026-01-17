from opennote import OpennoteClient

client = OpennoteClient(api_key="sk_opennote_c993f3a8-d86e-451c-9b9a-61d658379894")

response = client.video.create(model="picasso")
print(response)