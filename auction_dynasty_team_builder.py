import csv
from mip import Model, xsum, maximize, BINARY, CONTINUOUS, INTEGER


class Player:
    def __init__(self, position, name, salary, ppg):
        self.position = position
        self.name = name
        self.salary = salary
        self.ppg = ppg


def player_builder(file_path, position):
    players = []
    with open(file_path, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if row.get("ACQ", None) is None:
                continue
            if row["ACQ"] == "1":
                continue
            ppg = float(row["PPG"])
            salary = abs(float(row["VALUE"]) or float(row["ESTV"]))
            players.append(Player(position, row["Name"], salary, ppg))
    csv_file.close()
    return players


quarterbacks = player_builder(
    'C:\\Users\\Patrick\\Documents\\Auction_Draft_Values\\QB_Auction_Draft_Values2_2020.csv',
    "QB"
)

running_backs = player_builder(
    'C:\\Users\\Patrick\\Documents\\Auction_Draft_Values\\RB_Auction_Draft_Values2_2020.csv',
    "RB"
)

wide_receivers = player_builder(
    'C:\\Users\\Patrick\\Documents\\Auction_Draft_Values\\WR_Auction_Draft_Values2_2020.csv',
    "WR"
)

tight_ends = player_builder(
    'C:\\Users\\Patrick\\Documents\\Auction_Draft_Values\\TE_Auction_Draft_Values2_2020.csv',
    "TE"
)

qb_start = 0
qb_end = len(quarterbacks)
rb_start = qb_end
rb_end = rb_start + len(running_backs)
wr_start = rb_end
wr_end = wr_start + len(wide_receivers)
te_start = wr_end
te_end = te_start + len(tight_ends)

players = quarterbacks + running_backs + wide_receivers + tight_ends
print(len(quarterbacks))
print(len(running_backs))
print(len(wide_receivers))
print(len(tight_ends))

m = Model('auction_dynasty_team_builder')

player_picks = [m.add_var(var_type=BINARY, name="Player[{}]: Pos[{}]: PPG[{}]".format(player.name, player.position, player.ppg)) for player in quarterbacks + running_backs + wide_receivers + tight_ends]

flex_choices_1 = [m.add_var(var_type=BINARY, name="FLEX_CHOICE1[%d]" % i) for i in range(3)]
flex_choices_2 = [m.add_var(var_type=BINARY, name="FLEX_CHOICE2[%d]" % i) for i in range(3)]
flex_choices_3 = [m.add_var(var_type=BINARY, name="FLEX_CHOICE3[%d]" % i) for i in range(3)]
superflex_choices = [m.add_var(var_type=BINARY, name="SUPER_FLEX_CHOICE[%d]" % i) for i in range(4)]

m.objective = maximize(xsum(player.ppg * player_picks[idx] for idx, player in enumerate(players)))

m += xsum(player_picks[idx] * player.salary for idx, player in enumerate(players)) <= 390
# m += xsum(player_picks[i] for i in range(qb_start, qb_end)) == 2 - (superflex_choices[1] + superflex_choices[2] + superflex_choices[3])
m += xsum(player_picks[i] for i in range(qb_start, qb_end)) == 1 - (superflex_choices[1] + superflex_choices[2] + superflex_choices[3])
# m += xsum(player_picks[i] for i in range(rb_start, rb_end)) == 6 - (flex_choices_1[1] + flex_choices_1[2] + flex_choices_2[1] + flex_choices_2[2] + flex_choices_3[1] + flex_choices_3[2] + superflex_choices[0] + superflex_choices[2] + superflex_choices[3])
m += xsum(player_picks[i] for i in range(rb_start, rb_end)) == 5 - (flex_choices_1[1] + flex_choices_1[2] + flex_choices_2[1] + flex_choices_2[2] + flex_choices_3[1] + flex_choices_3[2] + superflex_choices[0] + superflex_choices[2] + superflex_choices[3])
# m += xsum(player_picks[i] for i in range(wr_start, wr_end)) == 6 - (flex_choices_1[0] + flex_choices_1[2] + flex_choices_2[0] + flex_choices_2[2] + flex_choices_3[0] + flex_choices_3[2] + superflex_choices[0] + superflex_choices[1] + superflex_choices[3])
m += xsum(player_picks[i] for i in range(wr_start, wr_end)) == 4 - (flex_choices_1[0] + flex_choices_1[2] + flex_choices_2[0] + flex_choices_2[2] + flex_choices_3[0] + flex_choices_3[2] + superflex_choices[0] + superflex_choices[1] + superflex_choices[3])
# m += xsum(player_picks[i] for i in range(te_start, te_end)) == 5 - (flex_choices_1[0] + flex_choices_1[1] + flex_choices_2[0] + flex_choices_2[1] + flex_choices_3[0] + flex_choices_3[1] + superflex_choices[0] + superflex_choices[1] + superflex_choices[2])
m += xsum(player_picks[i] for i in range(te_start, te_end)) == 4 - (flex_choices_1[0] + flex_choices_1[1] + flex_choices_2[0] + flex_choices_2[1] + flex_choices_3[0] + flex_choices_3[1] + superflex_choices[0] + superflex_choices[1] + superflex_choices[2])


m += xsum(flex_choices_1[i] for i in range(3)) == 1
m += xsum(flex_choices_2[i] for i in range(3)) == 1
m += xsum(flex_choices_3[i] for i in range(3)) == 1
m += xsum(superflex_choices[i] for i in range(4)) == 1


m.optimize()

if m.num_solutions:
    for i in range(len(player_picks)):
        if player_picks[i].x == 1:
            print(player_picks[i].name)
