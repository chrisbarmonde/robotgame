# hashlib math random operator itertools
import random
random.seed()

LOGGING_ENABLED = True

if LOGGING_ENABLED:
    import logging
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')

def log(message):
    if LOGGING_ENABLED:
        logging.debug(message)

def _sorted(l, field):
    a = [(item[field], item) for item in l]
    a.sort()
    return [item for _, item in a]


# @TODO automatically determine these I guess? I feel they should be provided...}
SPAWNS = (
    (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (5, 2), (6, 2), (12, 2), (13, 2), (3, 3), (4, 3),
    (14, 3), (15, 3), (3, 4), (15, 4), (2, 5), (16, 5), (2, 6), (16, 6), (1, 7), (17, 7),
    (1, 8), (17, 8), (1, 9), (17, 9), (1, 10), (17, 10), (1, 11), (17, 11), (2, 12), (16, 12),
    (2, 13), (16, 13), (3, 14), (15, 14), (3, 15), (4, 15), (14, 15), (15, 15), (5, 16), (6, 16),
    (12, 16), (13, 16), (7, 17), (8, 17), (9, 17), (10, 17), (11, 17)
)
OBSTACLES = (
    (0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0),
    (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (0, 1), (1, 1),
    (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1),
    (17, 1), (18, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (14, 2), (15, 2), (16, 2),
    (17, 2), (18, 2), (0, 3), (1, 3), (2, 3), (16, 3), (17, 3), (18, 3), (0, 4), (1, 4),
    (2, 4), (16, 4), (17, 4), (18, 4), (0, 5), (1, 5), (17, 5), (18, 5), (0, 6), (1, 6),
    (17, 6), (18, 6), (0, 7), (18, 7), (0, 8), (18, 8), (0, 9), (18, 9), (0, 10), (18, 10),
    (0, 11), (18, 11), (0, 12), (1, 12), (17, 12), (18, 12), (0, 13), (1, 13), (17, 13),
    (18, 13), (0, 14), (1, 14), (2, 14), (16, 14), (17, 14), (18, 14), (0, 15), (1, 15),
    (2, 15), (16, 15), (17, 15), (18, 15), (0, 16), (1, 16), (2, 16), (3, 16), (4, 16), (14, 16),
    (15, 16), (16, 16), (17, 16), (18, 16), (0, 17), (1, 17), (2, 17), (3, 17), (4, 17), (5, 17),
    (6, 17), (12, 17), (13, 17), (14, 17), (15, 17), (16, 17), (17, 17), (18, 17), (0, 18),
    (1, 18), (2, 18), (3, 18), (4, 18), (5, 18), (6, 18), (7, 18), (8, 18), (9, 18), (10, 18),
    (11, 18), (12, 18), (13, 18), (14, 18), (15, 18), (16, 18), (17, 18), (18, 18))


class Vector:
    def __init__(self, coords):
        self.x, self.y = coords

    def to_tuple(self):
        return self.x, self.y

    def clone(self):
        return Vector((self.x, self.y))

    def add(self, *args):
        if len(args) == 0:
            raise ValueError
        x, y = args[0] if isinstance(args[0], tuple) else args

        return Vector((self.x + x, self.y + y))

    def subtract(self, *args):
        if len(args) == 0:
            raise ValueError
        x, y = args[0] if isinstance(args[0], tuple) else args

        return Vector((self.x - x, self.y - y))

    def move_distance(self, *args):
        if len(args) == 0:
            raise ValueError
        x, y = args[0] if isinstance(args[0], tuple) else args

        return abs(self.x - x) + abs(self.y - y)


class PathFinder:
    adjacent = ((1, 0), (0, -1), (-1, 0), (0, -1))
    TYPES = {
        'SPAWN': 0,
        'OBSTACLE': 1,
        'FRIEND': 2,
        'ENEMY': 3,
        'OPEN': 4
    }


    def __init__(self, friends, enemies):
        self.friend_locations = [bot['location'] for bot in friends]
        self.enemy_locations = [bot['location'] for bot in enemies]

    def are_valid_coords(self, coords, allow_collision=False, allow_spawns=False):
        return (coords not in OBSTACLES
            and coords not in self.friend_locations
            and (coords not in SPAWNS or allow_spawns)
            and (coords not in self.enemy_locations or allow_collision))

    def _categorize_adjacent(self, coords):
        types = {_type: [] for _type in self.TYPES.values()}
        for movement in self.adjacent:
            path = Vector(coords).add(movement).to_tuple()
            if path in SPAWNS:
                types[self.TYPES['SPAWN']].append(path)
            elif path in OBSTACLES:
                types[self.TYPES['OBSTACLE']].append(path)
            elif path in self.friend_locations:
                types[self.TYPES['FRIEND']].append(path)
            elif path in self.enemy_locations:
                types[self.TYPES['ENEMY']].append(path)
            else:
                types[self.TYPES['OPEN']].append(path)
        return types


    def are_spawns_valid(self, bot):
        adjacent = self._categorize_adjacent(bot.location)
        return len(adjacent[self.TYPES['OPEN']]) == 0

    def get_best_path(self, bot, enemies, allow_collision=False):
        potential_paths = self.get_potential_paths(bot, enemies)
        allow_spawns = self.are_spawns_valid(bot)
        paths = [path for path in potential_paths
                 if self.are_valid_coords(path, allow_collision, allow_spawns)]

        if len(paths) == 0:
            if len(potential_paths) > 0:
                paths = [path for path in potential_paths
                         if path in self.friend_locations]
                if len(paths) > 0:
                    return self.find_adjacent_path(
                        bot, paths[0], allow_collision, allow_spawns)
            return self.find_open_path(bot)
        return paths[random.randint(0, len(paths) - 1)]

    def get_potential_paths(self, bot, enemies):
        by_hp = _sorted(enemies, 'hp')

        vector = bot.vector.subtract(by_hp[0]['location'])
        move_x = abs(vector.x) > 0
        move_y = abs(vector.y) > 0

        potential_paths = []
        if move_x:
            new_vector = bot.vector.add(-1 if vector.x > 0 else 1, 0).to_tuple()
            potential_paths.append(new_vector)

        if move_y:
            new_vector = bot.vector.add(0, -1 if vector.y > 0 else 1).to_tuple()
            potential_paths.append(new_vector)

        return potential_paths

    def find_adjacent_path(self, bot, coord, allow_collision=False, allow_spawns=False):
        vector = bot.vector.subtract(coord)
        rand = random.randint(1, 100) % 2

        if vector.x != 0:
            new_coords = bot.vector.add(0, 1 if rand else -1).to_tuple()
            if not self.are_valid_coords(new_coords, allow_collision, allow_spawns):
                new_coords = bot.vector.add((0, -1 if rand else 1)).to_tuple()
                if not self.are_valid_coords(new_coords, allow_collision, allow_spawns):
                    new_coords = self.find_open_path(bot)
        else:
            new_coords = bot.vector.add(1 if rand else -1, 0).to_tuple()
            if not self.are_valid_coords(new_coords, allow_collision, allow_spawns):
                new_coords = bot.vector.add((-1 if rand else 1, 0)).to_tuple()
                if not self.are_valid_coords(new_coords, allow_collision, allow_spawns):
                    new_coords = self.find_open_path(bot)

        return new_coords

    def find_open_path(self, bot):
        adjacent = self._categorize_adjacent(bot.location)
        open = adjacent[self.TYPES['OPEN']]
        if open:
            return open[random.randint(0, len(open) - 1)]

        spawns = adjacent[self.TYPES['SPAWN']]
        if spawns:
            return spawns[random.randint(0, len(spawns) - 1)]

        return None


class GameStrategy:
    def __init__(self):
        self.spawn_rate = 0
        self.spawn_count = 0
        self.spawn_wave = 0

        self.total_bots = 0
        self.friendly_bots = 0
        self.enemy_bots = 0
        self.bot_counter = 0

        self.last_total = 0

        self.bot_hp = 0
        self.attack_damage = (0, 0)
        self.collision_damage = 0
        self.suicide_damage = 0

        self.turn = 0

        self.friends = []
        self.enemies = []

    def get_closest_enemies(self, robot, game):
        closest_distance = None
        closest_enemies = []
        for location, bot in game['robots'].iteritems():
            if bot['player_id'] != robot.player_id:
                distance = robot.vector.move_distance(location)
                if closest_distance is None or distance < closest_distance:
                    closest_distance = distance
                    closest_enemies = [bot]
                elif distance == closest_distance:
                    closest_enemies.append(bot)

        return closest_enemies, closest_distance

    def get_attack_strategy(self, robot, enemies):
        if len(enemies) == 1:
            return ['attack', enemies[0]['location']]

        if robot.hp < self.bot_hp * 0.2 and len(enemies) > 1:
            return ['suicide']

        if len(enemies) == 3:
            coords = self.path_finder.find_open_path(robot)
            if coords:
                return ['move', coords]
            return ['suicide']

        if len([bot for bot in enemies if bot['hp'] < self.bot_hp]) == 0:
            return ['guard']

        by_hp = _sorted(enemies, 'hp')
        return ['attack', by_hp[0]['location']]

    def move_towards(self, robot, enemies, allow_collision=False):
        return self.path_finder.get_best_path(robot, enemies, allow_collision)

    def update(self, robot, game):
        if game['turn'] > self.turn:
            self._update_counts(robot, game)
            self.turn = game['turn']

            self.friends = [bot for bot in game['robots'].values()
                            if bot['player_id'] == robot.player_id]
            self.enemies = [bot for bot in game['robots'].values()
                            if bot['player_id'] != robot.player_id]

            self.path_finder = PathFinder(self.friends, self.enemies)
        #
        #if not robot.id:
        #    log("Assigning id {}".format(self.bot_counter))
        #    self.bot_counter += 1
        #    robot.id = self.bot_counter
        #    robot.spawn_wave = self.turn

    def update_movement(self, location, new_location):
        for friend in self.friends:
            if friend['location'] == location:
                friend['location'] = new_location
                return

    def _update_counts(self, robot, game):
        if robot.hp > self.bot_hp:
            self.bot_hp = robot.hp

        self.total_bots = len(game['robots'])
        self.friendly_bots = len([bot for bot in game['robots'].itervalues()
                                  if bot['player_id'] == robot.player_id])
        self.enemy_bots = self.total_bots - self.friendly_bots

        if not self.spawn_count:
            self.spawn_count = self.friendly_bots

strategy = GameStrategy()


class Robot:
    def __init__(self):
        self.id = None
        self.spawn_wave = 0
        self.vector = None

    def log(self, *args):
        if LOGGING_ENABLED:
            message = '[{}:{}]'.format(self.id, self.spawn_wave) + ''.join(str(arg) for arg in args)
            logging.debug(message)

    def pre_act(self):
        self.vector = Vector(self.location)

    def act(self, game):
        """
        self.location = (x, y)
        self.hp = int
        self.player_id = ??

        game={
            # a dictionary of all robots on the field mapped
            # by {location: robot}
            'robots': {
                (x1, y1): {
                    'location': (x1, y1),
                    'hp': hp,
                    'player_id': player_id,
                },

                # ...and the rest of the robots
            },

            # number of turns passed (starts at 0)
            'turn': turn
        }

        returns
            ['move', (x, y)]
            ['attack', (x, y)]
            ['guard']
            ['suicide']
        """

        # zone defensive scheme - robots stay in zone and wait
        # all out attack - go after whoever is nearest
        # avoidance - avoid at all costs
        # total defense - guard always, suicide when close to death
        # swarm - swarm nearby robot and destroy
        # decoy - draw off other bots and guard/suicide while others flank
        # attack weakest or strongest bots
        # group by spawn group?

        # how many bots?
        # when do they spawn?
        # how much hp?
        # how much damage per attack?
        # how much damage when guarding?
        # how much damage on suicide?
        # how much damage on collision?

        # might need to determine if enemy bot is going to suicide on near-death
        # suicide = # of bots surrounding * damage per bot > hp left
        # determine if bot is chasing after you - predict where he will be
        # determine: max hp, attack damage (from dealt and received) manually
        # determine: spawn amount + spawn time

        # @todo instead of moving to where bot is, move to closest open area next to bot

        # predict where enemy bots will go

        self.pre_act()
        strategy.update(self, game)
        enemies, distance = strategy.get_closest_enemies(self, game)
        if distance == 1:
            #self.log("Attacking", enemy['location'])
            action = strategy.get_attack_strategy(self, enemies)
        elif len(enemies) > 0:
            movement = strategy.move_towards(self, enemies)
            if movement == self.location:
                action = ['guard']
            else:
                #self.log('Moving', movement.to_tuple())
                strategy.update_movement(self.location, movement)
                action = ['move', movement]
        else:
            action = ['guard']

        return action

        #return ['suicide']
