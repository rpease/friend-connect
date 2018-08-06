from FakeDatabaseAPI import *

fakeAPI = FakeDatabaseAPI(r"test_data\city15000.csv","")
fakeAPI.load_users_table(r"test_data\users.csv")
fakeAPI.load_weight_table(r"test_data\weights.txt")

data = fakeAPI.get_user_destination_distance_matrix(True)
data = fakeAPI.get_scores(0)

print("done")