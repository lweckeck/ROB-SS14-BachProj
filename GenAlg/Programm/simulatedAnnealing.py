# coding=utf-8

from __future__ import division
import random
import math

import projConf
import fitness
import chromgen

class Dummy:
    num_generations = 1

def start(proj_conf, **args):
    algorithm = SimulatedAnnealing(proj_conf, **args)
    result = algorithm.simulate_annealing()

    algorithm.logger.info(repr(result))

#-----------------------------------------------------------
class SimulatedAnnealing(object):

    logger = None
    mode = None
    proj_conf = None
    fitness_args = None

    stepmax = None
    step = None
    start_temperature = None
    cooling_schedule = None
    cooling_schedule_alpha = None

    #-----------------------------------------------------------
    def __init__(self, proj_conf, **args):

        self.mode = proj_conf.get("mode", "Simulation")

        self.proj_conf = proj_conf
        self.logger = self.proj_conf.getClientLogger("simulatedAnnealing")
        self.fitness_args = { "proj_conf": proj_conf, "mode": self.mode}

        # Parameters for fitness evaluation
        self.parsed_kwargs = {}
        for item in proj_conf.cfg.items("fitness.evaluate_param"):
            self.parsed_kwargs[item[0]] = eval(item[1])
        numCurrents = int(proj_conf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["numCurrents"] = int(proj_conf.get_list("currents", "Simulation")[0])
        self.parsed_kwargs["proj_name"] = proj_conf.parseProjectConfig()["proj_name"]
        self.fitness_args.update(self.parsed_kwargs)

    #-----------------------------------------------------------
    def simulate_annealing(self):
        state = self.init_state()
        energy = self.calculate_energies([state])[0]

        best_state = state
        best_energy = energy
        self.logger.info("Starting with state " + str(state) + " and energy " + str(energy))

        self.step = 0
        self.stepmax = 5
        self.start_temperature = 10000
        self.cooling_schedule = "exponential"
        self.cooling_schedule_alpha = 0.5
        temperature = self.start_temperature

        while self.step < self.stepmax:
            self.logger.info("Beggining self.step " + str(self.step) + " of " + str(self.stepmax - 1))
            temperature = self.calculate_temperature(self.step / self.stepmax)
            self.logger.info("New temperature is " + str(temperature))

            new_state_candidates = self.neighbourList(state)
            new_state_energies = self.calculate_energies(new_state_candidates)

            for i in range(len(new_state_candidates)):
                self.step = self.step + 1
                if(self.probability(energy, new_state_energies[i], temperature) > random.random()):
                    state = new_state_candidates[i]
                    energy = new_state_energies[i]
                    self.logger.info("New state " + str(state) + " with energy " + str(energy) + " accepted")
                    break
                else:
                    self.logger.info("New state " + str(new_state_candidates[i]) + " with energy " + str(new_state_candidates[i]) + " NOT accepted")

            if energy > best_energy:
                best_state = state
                best_energy = energy

        return (best_state, best_energy)

    #-----------------------------------------------------------
    def init_state(self):

        chromosome = chromgen.generate_chromosome(random, self.fitness_args)
        return chromosome

    #-----------------------------------------------------------
    def calculate_energies(self, state_list):
        return fitness.evaluate_param(state_list, self.fitness_args)

    #-----------------------------------------------------------
    def calculate_temperature(self, r):

        if self.cooling_schedule == "exponential":
            temperature = self.start_temperature * pow(self.cooling_schedule_alpha, self.step)

        else:
            temperature = (1 - r) * self.start_temperature


        return temperature

    #-----------------------------------------------------------
    def neighbourList(self, state):

        # Select an allele to change
        allele = random.randint(0,10)

        if self.mode == "RS":
            while allele in [1,2]:
                allele = random.randint(0,10)

        if self.mode == "FS":
            while allele in [1,2,5,8]:
                allele = random.randint(0,10)

        # Random values determining the new value of the allele
        r_1 = random.random()
        r_2 = random.random()

        if r_1 < 0.5:
            new_value = ((chromgen.get_bounds(self.mode)[1])[allele] - state[allele]) * r_2
        else:
            new_value = (state[allele] - (chromgen.get_bounds(self.mode)[1])[allele]) * r_2

        state[allele] = new_value

        self.logger.info("Changing allele " + str(allele) + " to " + str(state[allele]))

        return [state]

    #-----------------------------------------------------------
    def probability(self, energy, new_energy, temperature):

        if new_energy >= energy:
            probability = 1

        else:
            probability = math.exp(-(energy - new_energy) / temperature)

        self.logger.info("Accepting probability: " + str(probability))

        return probability

