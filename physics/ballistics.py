


class Bullet():
    def __init__(self,
                 velocity,
                 position,
                 trajectory):
        self.velocity = velocity
        self.curr_position = position
        self.trajectory = trajectory

        self.prev_position = None

    def check_collision(self, world):
        # Check to see if there are any
        # objects or NPCs between the 
        # previous position of the bullet
        # and the current position
        pass

    def update_velocity(self, world):
        """
        Update velocity,
        taking into account wind direction and drag
        """
        # First account for drag
        drag = -world.drag_constant * self.velocity
        self.velocity += drag

        # ... and then wind direction
        self.velocity += world.get_wind(self.position)

        # ... and then finally gravity
        self.velocity[-1] += world.gravity_constant

    def update_position(self):
        self.prev_position = self.curr_position
        self.curr_position += self.velocity


class Gun():
    def __init__(self,
                 muzzle_velocity,
                 rate_of_fire,
                 magazine_capacity,
                 position):
        self.muzzle_velocity = muzzle_velocity
        self.rate_of_fire = rate_of_fire
        self.magazine_capacity = magazine_capacity
        self.position = position
        self.aim_axis = [0., 0., 0.]

    def update_player_position(self, x, y, z):
        self.position = [x, y, z]

    def update_aiming_axis(self, dx, dy, dz):
        """
        Update firing axis
        """
        self.aim_axis = [dx, dy, dz]

    def fire(self):
        """
        Fires gun, emitting a 'bullet' object
        """
        return Bullet(
            velocity=self.muzzle_velocity,
            position=self.position,
            trajectory=self.aim_axis
        )
