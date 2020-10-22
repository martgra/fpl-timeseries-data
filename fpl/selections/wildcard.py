import os

import numpy as np
import pandas as pd


class Wildcard:
    def __init__(self, dataframe, positions, population_size):
        self.population_size = population_size
        self.positions = positions
        self.team_costs = None
        self.teams_selected = None
        self.evaluation = None
        self.data = dataframe.to_numpy().reshape((self.positions[3], len(dataframe.columns)))
        self.players_sorted = [
            dataframe[0 : self.positions[0]].sort_values("value", ascending=False).to_numpy(),
            dataframe[self.positions[0] : self.positions[1]]
            .sort_values("value", ascending=False)
            .to_numpy(),
            dataframe[self.positions[1] : self.positions[2]]
            .sort_values("value", ascending=False)
            .to_numpy(),
            dataframe[self.positions[2] :].sort_values("value", ascending=False).to_numpy(),
        ]
        self.teams = self.generate_teams()
        self.evaluate_teams()
        self.run()

    def generate_teams(self):
        teams = []
        for j in range(self.population_size):
            team = []
            for i in range(1):
                team.append(self.data[np.random.randint(self.positions[0])].tolist())
            for i in range(3):
                team.append(
                    self.data[np.random.randint(self.positions[0], self.positions[1])].tolist()
                )
            for i in range(4):
                team.append(
                    self.data[np.random.randint(self.positions[1], self.positions[2])].tolist()
                )
            for i in range(3):
                team.append(
                    self.data[np.random.randint(self.positions[2], self.positions[3])].tolist()
                )
            teams.append(team)
        return np.array(teams)

    def evaluate_teams(self):
        evaluation = []
        cost_evaluation, team_cost = self.team_cost()
        rules, max_from_team, teams_selected = self.team_rules()
        for i in range(self.population_size):
            ev = np.sum(self.teams[i][:, 4])
            evaluation.append(ev)
        evaluation = evaluation * cost_evaluation * rules * max_from_team
        mean = np.mean(evaluation)
        delete = []
        for i in range(len(evaluation)):
            value = evaluation[i]
            if value < mean:
                delete.append(i)
        self.teams = np.delete(self.teams, delete, axis=0)
        self.evaluation = np.delete(evaluation, delete, axis=0)
        self.team_costs = np.delete(team_cost, delete, axis=0)
        self.teams_selected = np.delete(teams_selected, delete, axis=0)

    def team_cost(self):
        evaluation = []
        for i in range(len(self.teams)):
            ev = np.sum(self.teams[i][:, 3])
            evaluation.append(np.sum(ev))
        mean = np.mean(evaluation)
        high_cost = []
        for i in range(len(self.teams)):
            value = evaluation[i]
            if value > 835:
                high_cost.append(0)
            else:
                high_cost.append(1)
        return np.array(high_cost), np.array(evaluation)

    def team_rules(self):
        unique_players = []
        max_from_team = []
        teams_selected = []
        for i in range(len(self.teams)):
            team = self.teams[i]
            if np.any(np.diff(np.sort(team[:, 0], axis=0), axis=0) == 0):
                unique_players.append(0)
            else:
                unique_players.append(1)
            keys, values = np.unique(team[:, 2], axis=0, return_counts=True)
            if np.max(values) > 3:
                max_from_team.append(0)
            else:
                max_from_team.append(1)
            teams_selected.append(dict(zip(keys, values)))
        return np.array(unique_players), np.array(max_from_team), np.array(teams_selected)

    def get_player(self, player, team, team_position, new_players):
        players = self.players_sorted[int(player[1]) - 1]
        for i in range(len(players)):
            new_player = players[i]
            if new_player[0] in new_players:
                continue
            if new_player[0] in team[:, 0]:
                continue
            if new_player[3] - player[3] + self.team_costs[team_position] > 835:
                continue
            if new_player[2] == player[2]:
                return new_player
            if new_player[2] in self.teams_selected[team_position].keys():
                if self.teams_selected[team_position][int(new_player[2])] == 3:
                    continue
                else:
                    self.teams_selected[team_position][int(new_player[2])] += 1
                    self.teams_selected[team_position][int(player[2])] += -1
                    return new_player
            else:
                self.teams_selected[team_position][int(new_player[2])] = 1
                self.teams_selected[team_position][int(player[2])] += -1
                return new_player
        return player

    def crossover(self, team1, team2):
        cut = np.random.randint(11)
        return np.concatenate((team1[:cut, :], team2[cut:, :]))

    def mutate(self, team, team_position):
        substitutes = np.random.randint(2)
        team = team[team[:, len(team[0]) - 1].argsort()]
        new_players = []
        new_team = []
        for i in range(substitutes, len(team)):
            new_team.append(team[i])
        for i in range(substitutes):
            player = team[i]
            new_player = self.get_player(player, team, team_position, new_players)
            new_team.append(new_player)
            new_players.append(new_player[0])
            self.team_costs[team_position] = (
                self.team_costs[team_position] + new_player[3] - player[3]
            )
        new_team = np.array(new_team)
        return new_team[new_team[:, 1].argsort()]

    def run(self):
        best_team_index = np.argmax(self.evaluation)
        best_team = [self.teams[best_team_index], self.evaluation[best_team_index]]
        convergation = 0
        while convergation < 10:
            new_population = []
            for j in range(len(self.teams)):
                team = self.teams[j]
                new_population.append(self.mutate(team, j))
            while len(new_population) < self.population_size:
                team1 = new_population[np.random.randint(len(self.teams))]
                team2 = new_population[np.random.randint(len(self.teams))]
                child = self.crossover(team1, team2)
                new_population.append(child)
            self.teams = np.array(new_population)
            self.evaluate_teams()
            print("Length of teams", len(self.teams), "best team", best_team[1])
            bti = np.argmax(self.evaluation)
            if self.evaluation[bti] > best_team[1]:
                best_team[0] = self.teams[bti]
                best_team[1] = self.evaluation[bti]
                convergation = 0
            else:
                convergation += 1
