from math import sqrt

from mathutils import Vector

#from ai_utils import single_ray_collision_detection
import entities


class Actor(entities.EntityBase):
	""" An actor is anything that the event manager needs to control.
	Actors should inherit this class instead of EntityBase.

	This class defines some basic commands for the event manager to
	be able send actors where it needs to.
	"""

	def __init__(self):
		super().__init__()

		self.walk_speed = 10
		self.run_speed = 10
		self.walking = True

		self.health = 100
		self.faction = 1

		self.path = []
		self.point_of_interest = None

	def move_to(self, point):
		""" Walk the actor from its current location to some point """
		navmesh = self.find_navmesh()

		if not navmesh:
			# There is no navmesh
			self.path = [self.worldPosition.copy(), point]
			return

		# Check to see if actor is on a navmesh
		test = navmesh.findPath(self.worldPosition, self.worldPosition)
		diff = test[-1] - self.worldPosition
		actor_on_navmesh = sqrt(diff[0] ** 2 + diff[1] ** 2) < 0.5  # Ignoring z difference

		# Check to see if point is on a navmesh
		test = navmesh.findPath(point, point)
		diff = test[-1] - point
		point_on_navmesh = sqrt(diff[0] ** 2 + diff[1] ** 2) < 0.5  # Ignoring z difference

		# Construct a path from the actor's position to the point
		if actor_on_navmesh and point_on_navmesh:
			# The path lies entirely on the navmesh
			path = navmesh.findPath(self.worldPosition, point)

		elif actor_on_navmesh and not point_on_navmesh:
			# The second half of the path lies off the navmesh
			path = navmesh.findPath(self.worldPosition, point)
			path.append(point)

		elif not actor_on_navmesh and point_on_navmesh:
			# The first half of the path lies off the navmesh
			path = [self.worldPosition.copy()]
			path.extend(navmesh.findPath(self.worldPosition, point))

		else:
			# The entire path is off the navmesh
			path = navmesh.findPath(self.worldPosition, point)

			if path[0] == path[1]:
				# The path doesn't cross over the navmesh
				path = [self.worldPosition.copy(), Vector(point)]

			else:
				# The path is partially covered by the navmesh
				path.insert(self.worldPosition.copy(), 0)
				path.append(Vector(point))

		self.path = path

	def look_at(self, point):
		self.point_of_interest = point

	def play_animation(self, anim):
		pass

	def update_path_follow(self):
		""" If following a path, move the actor along it """
		# TODO - checks for if the actor has overshot the next node
		current = self.path[0]
		diff = current - self.worldPosition
		if diff.magnitude < 1.3:
			# Actor has reached the current node
			self.path.pop(0)
			if self.path:
				current = self.path[0]
				diff = current - self.worldPosition
			else:
				return

		# TODO - allow run speeds
		# hit_ob, point, normal = single_ray_collision_detection(self, )
		#if diff.magnitude < self.walk_speed / 3:
			#desired_vel = diff * 3
		#else:
		desired_vel = diff.normalized() * self.walk_speed
		actual_vel = self.worldLinearVelocity

		d_vel = desired_vel - actual_vel
		d_vel.z = 0  # TODO - apply force perpendicular to ground normal

		vel = diff.normalized() * self.walk_speed

		self.worldLinearVelocity = vel

		self.alignAxisToVect(self.worldLinearVelocity, 1, 0.5)
		self.alignAxisToVect([0, 0, 1], 2, 1)

	def update_look_at(self):
		target = self.point_of_interest.to_2d() - self.worldPosition.to_2d()

		self.alignAxisToVect(target.to_3d(), 1, 0.05)

		ori = self.worldOrientation[1].to_2d()
		ori.x *= -1

		if ori.angle(target) < 0.16:
			self.point_of_interest = None

	def main(self):
		super().main()

		if self.path:
			self.update_path_follow()

		if self.point_of_interest:
			self.update_look_at()
