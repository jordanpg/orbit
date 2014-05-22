import pygame, math, random
from pygame.locals import *

AU = (149.6e6 * 1000)
BACK = (0, 0, 0)
ARROWS = False
ARROWSCALEFACTOR = 2
MASSFACTOR = (4.0 / 0.5)
SCALEFACTOR = 250 / AU
GRAV = 6.67e-11
TRAILS = 100
CRASHCOLOUR = (255, 165, 0)
VECDRAWSCALE = (1.0 / 64.0)
CRASHTOLERANCE = 0.25

def trunc(f, n):
    '''Truncates/pads a float f to n decimal places without rounding'''
    slen = len('%.*f' % (n, f))
    return str(f)[:slen]

def invert(c):
	return (255-c[0], 255-c[1], 255-c[2])

def VectorAdd(a, b):
	return (a[0] + b[0], a[1] + b[1])

def VectorSub(a, b):
	return (a[0] - b[0], a[1] - b[1])

def VectorScale(a, v):
	return (a[0] * v, a[1] * v)

def VectorDist(a, b):
	dx = b[0] - a[0]
	dy = b[1] - a[1]
	return math.sqrt(dx**2 + dy**2)

def VectorLen(a):
	return math.sqrt(a[0]**2 + a[1]**2)

def VectorNormalise(a):
	l = VectorLen(a)
	x = a[0] / l
	y = a[1] / l
	return (x, y)

def VectorDot(a, b):
	return (a[0] * b[0] + a[1] * b[1])

def VectorInt(a):
	return (int(a[0]), int(a[1]))

def VectorFloat(a):
	return (float(a[0]), float(a[1]))


class Object(pygame.sprite.Sprite):
	def __init__(self, rend, scale, position, mass, colour=(255,255,255), fixed=False, maxTrails=TRAILS, crash=True, grav=True):
		pygame.sprite.Sprite.__init__(self)

		# print scale
		self.rend = rend
		# self.trail = rend.trails
		self.screen = rend.screen
		self.radius = scale / 2
		self.img = pygame.Surface((scale, scale))
		self.rect = self.img.get_rect(center=position)
		# self.rect.x = position[0] - self.radius
		# self.rect.y = position[1] - self.radius
		self.position = position
		self.pos = position
		self.rpos = position
		self.vel = (0.0, 0.0)
		self.colour = colour
		self.scale = scale
		self.arrow = pygame.Surface(VectorScale((10,10), ARROWSCALEFACTOR))
		self.mass = mass
		self.trails = []
		self.fixed = fixed
		self.maxTrails = maxTrails
		self.crash = crash
		self.crashed = False
		self.grav = grav
		
		# print self.img

	def render(self):
		# print "a"
		rad = self.scale / 2
		# print rad
		self.img.fill(BACK)
		pygame.draw.circle(self.img, self.colour, (rad, rad), rad)
		self.img.set_colorkey(BACK)
		self.screen.blit(self.img, self.rect)

		if ARROWS and VectorLen(self.vel) > 0:
			# print self, VectorLen(self.vel)
			self.drawArrow()

		if len(self.trails) > 1:
			self.drawTrails()

	def drawArrow(self):
		norm = VectorNormalise(self.vel)
		add = VectorScale(norm, self.scale)
		start = VectorAdd(self.rect.center, add)
		vec = VectorScale(self.vel, ARROWSCALEFACTOR)
		end = VectorAdd(self.rect.center, vec)
		# print self.rect.center
		# print end
		pygame.draw.line(self.screen, self.colour, start, end, ARROWSCALEFACTOR)

		self.arrow.fill(BACK)
		pygame.draw.line(self.arrow, self.colour, (0, 0), VectorScale((5, 5), ARROWSCALEFACTOR), ARROWSCALEFACTOR)
		pygame.draw.line(self.arrow, self.colour, VectorScale((0, 10), ARROWSCALEFACTOR), VectorScale((5, 5), ARROWSCALEFACTOR), ARROWSCALEFACTOR)
		self.arrow.set_colorkey(BACK)

		ang = math.atan2(-(start[1] - end[1]), start[0] - end[0])
		ang = math.degrees(ang)

		nar = pygame.transform.rotate(self.arrow, ang)
		nrect = nar.get_rect(center=start)
		self.screen.blit(nar, nrect)

	def getPos(self):
		return self.pos[0],self.pos[1]

	def getRPos(self):
		return self.rpos[0],self.rpos[1]

	def setPos(self, val, rp=False):
		try:
			self.pos = (val[0], val[1])
			if rp:
				self.rpos = (val[0], val[1])
			self.rect.x = val[0]
			self.rect.y = val[1]
			return True
		except:
			return False

	def getVel(self):
		return self.vel[0],self.vel[1]

	def setVel(self, val):
		if self.fixed:
			val = (0, 0)
		self.vel = (val[0], val[1])
		# print val
		return True

	def addVel(self, val):
		try:
			x = self.vel[0] + val[0]
			y = self.vel[1] + val[1]
			self.setVel((x, y))
		except:
			pass

		return self.vel

	def addTrail(self):
		pos = self.rect.center
		if len(self.trails) > 0 and pos == self.trails[-1] and not self.crashed:
			return
		if not self.crashed:
			self.trails.append(self.rect.center)
		# print self.trails
		if len(self.trails) > self.maxTrails:
			self.trails.pop(0)

		if len(self.trails) > 0 and self.crashed:
			self.trails.pop(0)

	def drawTrails(self):
		pygame.draw.lines(self.screen, self.colour, False, self.trails)

	def physCheck(self):
		for i in self.rend.objects:
			if i == self or not i.grav:
				continue
			r = pygame.sprite.collide_rect(self, i)
			# print r
			if r:
				fmass = self.mass * CRASHTOLERANCE
				if fmass > i.mass:
					continue
				self.crashObj()
				return

	def update(self):
		l = VectorLen(self.vel)
		if l > 0:
			x = self.rpos[0] + self.vel[0]
			y = self.rpos[1] + self.vel[1]
			# print x, y
			self.rpos = x, y
			self.setPos(VectorInt((x, y)))

		self.addTrail()

		if self.crash:
			self.physCheck()

		if self.crashed and len(self.trails) < 1:
			self.delete()

		if not self.alive():
			self.delete()

		self.render()

	def crashObj(self):
		if self.rend.drawObj == self:
			self.rend.cancelDraw(False)
		self.crashed = True
		self.colour = CRASHCOLOUR
		self.setVel((0, 0))
		self.fixed = True
		# self.grav = False


	def delete(self):
		if self in self.rend.objects:
			self.rend.objects.remove(self)
		self.kill()


class Render:
	def __init__(self, res=(1280,720), title="PyGame"):
		self.screen = pygame.display.set_mode(res, 0, 32)
		pygame.display.set_caption(title)
		pygame.init()
		pygame.mouse.set_visible(True)

		self.res = res
		self.title = title
		self.entities = pygame.sprite.Group()
		self.objects = []
		# self.trails = pygame.Surface(res)

		self.newBody = True
		self.drawing = False
		self.drawObj = None
		self.drawStart = (0,0)
		self.arrow = pygame.Surface(VectorScale((10,10), ARROWSCALEFACTOR))

		self.doReset = True

	def addElement(self, objList=[]):
		for obj in objList:
			if self.entities.has(obj):
				continue
			self.entities.add(obj)
			self.objects.append(obj)

	def render(self):
		self.screen.fill(BACK)
		# pygame.draw.lines(self.screen, (255, 255, 255), False, [(0,0), (50,50), (0,20)])
		# self.trails.fill(BACK)
		# self.trails.set_colorkey(BACK)
		mpos = pygame.mouse.get_pos()
		if self.drawing:
			self.drawArrow(self.drawStart, mpos)

		for obj in self.objects:
			obj.update()

		font = pygame.font.Font("uniball_sans.ttf", 32)
		text = font.render("FPS: " + trunc(self.clock.get_fps(), 1) + "; Bodies: " + str(len(self.objects)) + "; Active Bodies: " + str(self.getActiveBodies()), 1, invert(BACK))
		text2 = font.render("Click and hold to create a new body; Press R to reset", 1, invert(BACK))
		text4 = font.render("Press ESC to quit", 1, invert(BACK))
		self.screen.blit(text, (0, 0))
		self.screen.blit(text2, (0, 20))
		self.screen.blit(text4, (self.res[0]-(text4.get_width()+4), self.res[1]-28))
		if self.drawing:
			text3 = font.render("Body Mass: " + str(self.drawObj.mass) + "; Drawn Velocity: " + str(self.solveVec(self.drawStart, mpos)), 1, invert(BACK))
			self.screen.blit(text3, (0, 40))

		pygame.display.flip()

	def calcAtt(self, i, j):
		ip = i.getRPos()
		jp = j.getRPos()
		dx = jp[0] - ip[0]
		dy = jp[1] - ip[1]
		d = math.sqrt(dx**2 + dy**2)

		if d == 0:
			return (0, 0)

		f = GRAV * i.mass * j.mass / d**2

		th = math.atan2(dy, dx)
		fx = math.cos(th) * f
		fy = math.sin(th) * f
		# print fx, fy
		return fx, fy

	def calcAtts(self, obj):
		if not self.entities.has(obj):
			return (0, 0)

		vel = (0, 0)
		for j in self.objects:
			if j == obj or not j.grav:
				continue

			val = self.calcAtt(obj, j)
			x = vel[0] + val[0]
			y = vel[1] + val[1]
			vel = (x, y)

		return VectorScale(vel, 1 / SCALEFACTOR)

	def moveBodies(self):
		if len(self.objects) < 2:
			return
		v = {}
		for obj in self.objects:
			if not obj.grav:
				continue
			v[obj] = self.calcAtts(obj)

		for obj in self.objects:
			if not obj.grav:
				continue
			obj.addVel(VectorScale(v[obj], obj.mass**-1))

	def getActiveBodies(self):
		val = len(self.objects)
		for i in self.objects:
			if i.crashed or not i.grav:
				val -= 1

		return val

	def solveVec(self, start, end):
		vec = VectorFloat(VectorSub(end, start))
		val = VectorScale(vec, VECDRAWSCALE)
		return val

	def drawArrow(self, start, end):
		# print "a"
		pygame.draw.line(self.screen, self.drawObj.colour, start, end, ARROWSCALEFACTOR)

		self.arrow.fill(BACK)
		pygame.draw.line(self.arrow, self.drawObj.colour, (0, 0), VectorScale((5, 5), ARROWSCALEFACTOR), ARROWSCALEFACTOR)
		pygame.draw.line(self.arrow, self.drawObj.colour, VectorScale((0, 10), ARROWSCALEFACTOR), VectorScale((5, 5), ARROWSCALEFACTOR), ARROWSCALEFACTOR)
		self.arrow.set_colorkey(BACK)

		ang = math.atan2(-(start[1] - end[1]), start[0] - end[0])
		ang = math.degrees(ang)

		nar = pygame.transform.rotate(self.arrow, ang+180)
		nrect = nar.get_rect(center=end)
		self.screen.blit(nar, nrect)

	def drawBegin(self, pos):
		m = random.randrange(1, 9000)
		self.drawObj = Object(self, int(solveMassScale(m)), pos, m, (random.randrange(0,255), random.randrange(0,255), random.randrange(0, 255)), grav=False, crash=False)
		self.addElement([self.drawObj])
		self.drawStart = pos
		self.drawing = True

	def drawFinish(self, pos):
		if not self.drawObj:
			return

		val = self.solveVec(self.drawStart, pos)
		# print val
		self.drawObj.setVel(val)
		self.drawObj.setPos(self.drawStart, True)
		# self.drawObj.grav = True
		# self.drawObj = None
		# self.drawStart = (0, 0)
		self.drawing = False

	def cancelDraw(self, kill=True):
		self.drawing = False
		if self.drawObj and kill:
			self.drawObj.delete()
		self.drawObj = None
		self.drawStart = (0, 0)

	def loop(self):
		self.clock = pygame.time.Clock()
		running = True
		while running:
			pygame.event.get()
			self.clock.tick(60)
			keyboard = pygame.key.get_pressed()
			mouse = pygame.mouse.get_pressed()
			mpos = pygame.mouse.get_pos()
			if keyboard[pygame.K_ESCAPE]:
				running = False

			if keyboard[pygame.K_r]:
				if self.doReset == True:
					self.doReset = False
					self.start()
			else:
				self.doReset = True

			if mouse[0]:
				if self.newBody == True:
					self.newBody = False
					self.drawBegin(mpos)
				# elif self.drawing:
				# 	self.drawArrow(self.drawStart, mpos)
			else:
				if self.drawing:
					self.drawFinish(mpos)

				self.newBody = True

			self.moveBodies()

			if not self.drawing and self.drawObj:
				self.drawObj.setPos(self.drawStart, True)
				self.drawObj.crash = True
				self.drawObj.grav = True
				self.drawObj = None
				self.drawStart = (0, 0)

			self.render()

	def start(self):
		l = len(self.objects)
		if l > 0:
			while len(self.objects) > 0:
				self.objects[0].delete()

		m = 1e2
		b = Object(rend, 16, (480, rend.res[1]/2), m, (0, 75, 0))
		b.setVel((0, 2.75))

		m = 8.5e1
		h = Object(rend, 16, (360, rend.res[1]/2), m, (75, 0, 75))
		h.setVel((-0.01, 2))

		m = 15
		g = Object(rend, 4, (240, rend.res[1]/2), m, (75, 75, 75), maxTrails=500, crash=True)
		g.setVel((0, -1.5))

		m = 3e4
		c = Object(rend, 64, (rend.res[0]/2, rend.res[1]/2), m, fixed=True, crash=False)
		self.addElement([b, c, h, g])

def solveMassScale(mass):
	# print MASSFACTOR
	pl = len(str(mass))
	s = pl * MASSFACTOR
	return s

rend = Render(title="Orbit")

rend.start()

rend.loop()

pygame.quit()