import json
def process_game(data):
  game_instance = data.get('gameinstanceid')
  game_timestamp = data.get('gamedatatimestamp')

  print('[{}] Game Instance ID obtained from /game_end request: {}'.format(game_timestamp, game_instance))

  if game_instance is None or not isinstance(game_instance, int):
    return {"error": "Invalid or missing game_instance"}

  # Call the main function ...

  return {"message": "Game end processed successfully"}

data_str=oidlUtils.parameters.getParameter("DATA", "{\"gameinstanceid\":0,\"gamedatatimestamp\":\"1757093771\"}")

data=json.loads(data_str)
r=process_game(data)
print(r)