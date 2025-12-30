import pygame
import os
from copy import deepcopy as dc

pygame.init()

screen = pygame.display.set_mode((600, 500), pygame.RESIZABLE)
# Simulated Tile logic
pygame.display.set_caption('STlogic')

font = pygame.font.SysFont('consolas', 30)

def get_image(png):
	return pygame.image.load(f'assets\\{png}.png').convert_alpha()
pygame.display.set_icon(get_image('STlogic'))

def img(sq):
	t = sq[2]
	o = sq[3]
	r = sq[4]

	if r > 0:
		return pygame.transform.rotate(get_image(f'{t}-{o}'), 90 * r)
	
	return get_image(f'{t}-{o}')

#   1
# 2 # 0
#   3

def checksq(sq):
	x = sq[0]
	y = sq[1]

	s1 = G[(x + 1) % len(G)][y]
	s2 = G[x][(y - 1) % len(G[x])]
	s3 = G[(x - 1) % len(G)][y]
	s4 = G[x][(y + 1) % len(G[x])]

	return ((s1[2], s2[2], s3[2], s4[2]), (s1[3], s2[3], s3[3], s4[3]), (s1[4], s2[4], s3[4], s4[4]))

TYPES = {
	#Empty#
	0: (15, 15, 15),

	#Wire#
	1: (255, 255, 255),

	#Split#
	2: (200, 200, 200),
	
	#Bridge#
	3: (255, 128, 32),

	#Not#
	4: (255, 0, 0),

	#And#
	5: (0, 90, 255),

	#Input#
	6: (0, 255, 0),

	#Output#
	7: (157, 0, 255),
}

Z = []
Y = []

N = []
G = []
for x in range(50):
	N.append([])
	G.append([])
	for y in range(50):
		# x, y, type, on/off, rotation

		N[x].append([x, y, 0, 0, 0])
		G[x].append([x, y, 0, 0, 0])

srf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
srf.set_alpha(128)

C = []
S = []
Scc = []

CAM = [0,0,1]
CAMtemp = [0,0]
Mtemp = [0,0]
moveCAM = False

seltype = 1
R = 0

selsq = []
selrec = ()

PLAY = False
CTRL = False
SHIFT = False
SAVE = False
LOAD = False

currSave = None

#=Typical=Loop=====================================================================================================

running = True
while running:
	og = [screen.get_size()[0] / 2, screen.get_size()[1] / 2]
	mousepos = pygame.mouse.get_pos()

	srf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
	#srf.set_alpha(128)
	
	screen.fill((0, 0, 0))

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False

		if event.type == pygame.KEYDOWN:
			
			#=Select=Color==============================#

			if ord('1') <= event.key <= ord(str(len(TYPES.keys()) - 1)):
				seltype = int(chr(event.key))
			if event.key == ord('q'):
				R = (R + 1) % 4
			if event.key == ord('e'):
				R = (R - 1) % 4

			#=Play=======================================#

			if event.key == 32 and not SHIFT:
				PLAY = not PLAY

				if PLAY:
					g = dc(G)
					Z.append((1, g))
					Y.clear()

			#=Ctrl=======================================#

			if event.key == pygame.K_LCTRL:
				CTRL = True

			#=SHIFT======================================#

			if event.key == pygame.K_LSHIFT and not PLAY:
				SHIFT = not SHIFT
				S.clear()

			#=Undo=======================================#

			if event.key == ord('z') and CTRL and len(Z) > 0 and not PLAY:
				z = Z[-1]
				Z.pop()

				if z[0] == 0:
					Y.append((0, tuple(z[1]), G[z[1][0]][z[1][1]]))

					#print(z)
					G[z[1][0]][z[1][1]] = z[2]

					if C.count((z[1][0], z[1][1])) == 0:
						C.append((z[1][0], z[1][1]))

					elif z[2] == 0:
						C.remove((z[1][0], z[1][1]))
				if z[0] == 1:
					Y.append((1, dc(G)))

					G.clear()
					G.extend(z[1])

			#=Redo=======================================#

			if event.key == ord('y') and CTRL and len(Y) > 0 and not PLAY:
				#print(Y)
				y = Y[-1]
				Y.pop()

				if y[0] == 0:
					Z.append((0, tuple(y[1]), G[y[1][0]][y[1][1]]))

					G[y[1][0]][y[1][1]] = y[2]

					if C.count((y[1][0], y[1][1])) == 0:
						C.append((y[1][0], y[1][1]))

					elif y[2] == 0:
						C.remove((y[1][0], y[1][1]))

				if y[0] == 1:
					Z.append((1, dc(G)))

					G.clear()
					G.extend(y[1])

			#=Save=======================================#

			if event.key == ord('s') and CTRL and not PLAY:
				SAVE = True

			#=Load=======================================#

			if event.key == ord('o') and CTRL and not PLAY:
				LOAD = True

			#=Copy=======================================#

			if event.key == ord('c') and CTRL and SHIFT and len(S) == 3:
				Scc = dc(S[2])
				#print(f'copied: {S[0]} to {S[1]}')#\n{Scc}')
				S.clear()

			#=Paste======================================#

			if event.key == ord('v') and CTRL and SHIFT and len(Scc) * len(selsq) > 0:
				Z.append((1, dc(G)))
				Y.clear()

				frosq = tuple(selsq)
				if len(S) > 0:
					frosq = S[0]

				for x in range(len(Scc)):
					for sq in Scc[x]:
						if sq[2] != 0:
							nsq = [frosq[0] + sq[0] - Scc[0][0][0], frosq[1] + sq[1] - Scc[0][0][1]]
							nsq.extend(sq[2:])
							G[nsq[0]][nsq[1]] = nsq.copy()
							C.append(nsq[:2])
				
				#print(frosq, Scc, '\n\n')
				S.clear()

			#============================================#

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LCTRL:
				CTRL = False

		if event.type == pygame.MOUSEBUTTONDOWN:

			#=Lclick=====================================#

			if event.button == 1:
				if len(selsq) > 0:
					#=Activate=Inputs=#
					if PLAY:
						if G[selsq[0]][selsq[1]][2] == 6:
							G[selsq[0]][selsq[1]][3] = int(not G[selsq[0]][selsq[1]][3])
					#=Select=#
					elif SHIFT:
						if len(S) == 3:
							S.clear()

						S.append(tuple(selsq[:2]))
						if len(S) == 2:
							ltemp = []
							for x in range(abs(S[0][0] - S[1][0]) + 1):
								ltemp.append([])
								for y in range(abs(S[0][1] - S[1][1]) + 1):
									ltemp[x].append(G[x + min(S[0][0], S[1][0])][y + min(S[0][1], S[1][1])])
							S.append(ltemp)

						#print(S)
					#=Place=#
					else:
						if G[selsq[0]][selsq[1]][2] != seltype:
							Z.append((0, tuple(selsq), dc(G[selsq[0]][selsq[1]])))

						G[selsq[0]][selsq[1]][2] = seltype
						G[selsq[0]][selsq[1]][4] = R

						if C.count((selsq[0],selsq[1])) == 0:
							C.append((selsq[0],selsq[1]))

						Y.clear()
				elif SHIFT:
					S.clear()

			#=Pan========================================#

			if event.button == 2:
				CAMtemp[0] = CAM[0]
				CAMtemp[1] = CAM[1]
				Mtemp[0] = mousepos[0]
				Mtemp[1] = mousepos[1]
				
				moveCAM = True

			#=Rclick=====================================#

			if event.button == 3:
				if len(selsq) > 0 and not PLAY:
					if G[selsq[0]][selsq[1]][2] != 0:
						Z.append((0, tuple(selsq), dc(G[selsq[0]][selsq[1]])))

					G[selsq[0]][selsq[1]][2] = 0
					G[selsq[0]][selsq[1]][3] = 0

					try:
						C.remove(tuple(selsq))
						Y.clear()

					except ValueError:
						pass

			#=Zoom=======================================#

			if event.button == 4:
				if CAM[2] < 9:
					CAM[2] += .1

			if event.button == 5:
				if CAM[2] > .2:
					CAM[2] -= .1

			#============================================#

		if event.type == pygame.MOUSEBUTTONUP:
			if event.button == 2:
				moveCAM = False

	#=Panning=#

	if moveCAM:
		CAM[0] = CAMtemp[0] + (mousepos[0] - Mtemp[0]) / CAM[2]
		CAM[1] = CAMtemp[1] + (mousepos[1] - Mtemp[1]) / CAM[2]

#=Tile=Loop========================================================================================================

	N = dc(G)

	if PLAY:
		for s in C:
			sq = N[s[0]][s[1]]
			dir = sq[4]
			nbrs = checksq(sq)

			match sq[2]:
				#=And=#
				case 5:
					sq[3] = 0

					dirs2rcv = ((dir - 1) % 4, (dir + 1) % 4)
					rcvtyps = (nbrs[0][dirs2rcv[0]], nbrs[0][dirs2rcv[1]])
					rcvpwrs = (nbrs[1][dirs2rcv[0]], nbrs[1][dirs2rcv[1]])
					rcvdirs = (nbrs[2][dirs2rcv[0]], nbrs[2][dirs2rcv[1]])

					inputs = [0, 0]

					for i in (0,1):
						match rcvtyps[i]:
							case 2:
								if rcvdirs[i] != dirs2rcv[i] and rcvpwrs[i] == 1:
									inputs[i] = 1
							case 4:
								if rcvdirs[i] == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] == 0:
									inputs[i] = 1
							case 7:
								pass
							case 3:
								if rcvdirs[i] == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] in (1,3):
									inputs[i] = 1

								elif (rcvdirs[i] + 1) % 4 == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] in (2,3):
									inputs[i] = 1
							case _: 
								if rcvdirs[i] == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] == 1:
									inputs[i] = 1

					match tuple(inputs):
						case (0, 0):
							sq[3] = 0
						case (0, 1):
							sq[3] = 2
						case (1, 0):
							sq[3] = 3
						case (1, 1):
							sq[3] = 1
				#=Input=#
				case 6:
					pass

				#=Bridge=#
				case 3:
					sq[3] = 0

					dirs2rcv = ((dir - 2) % 4, (dir - 1) % 4)
					rcvtyps = (nbrs[0][dirs2rcv[0]], nbrs[0][dirs2rcv[1]])
					rcvpwrs = (nbrs[1][dirs2rcv[0]], nbrs[1][dirs2rcv[1]])
					rcvdirs = (nbrs[2][dirs2rcv[0]], nbrs[2][dirs2rcv[1]])

					inputs = [0, 0]

					for i in (0,1):
						match rcvtyps[i]:
							case 2:
								if rcvdirs[i] != dirs2rcv[i] and rcvpwrs[i] == 1:
									inputs[i] = 1
							case 4:
								if rcvdirs[i] == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] == 0:
									inputs[i] = 1
							case 7:
								pass
							case 3:
								if rcvdirs[i] == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] in (1,3):
									inputs[i] = 1

								elif (rcvdirs[i] + 1) % 4 == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] in (2,3):
									inputs[i] = 1
							case _: 
								if rcvdirs[i] == (dirs2rcv[i] + 2) % 4 and rcvpwrs[i] == 1:
									inputs[i] = 1

					match tuple(inputs):
						case (0, 0):
							sq[3] = 0
						case (0, 1):
							sq[3] = 2
						case (1, 0):
							sq[3] = 1
						case (1, 1):
							sq[3] = 3

				#=Other=Tiles=#
				case _:
					sq[3] = 0
					dir2rcv = (dir + 2) % 4
					rcvtyp = nbrs[0][dir2rcv]
					rcvpwr = nbrs[1][dir2rcv]
					rcvdir = nbrs[2][dir2rcv]

					match rcvtyp:
						case 2:
							if rcvdir != dir2rcv and rcvpwr == 1:
								sq[3] = 1
						case 4:
							if rcvdir == dir and rcvpwr == 0:
								sq[3] = 1
						case 7:
							pass
						case 3:
							if rcvdir == dir and rcvpwr in (1,3):
								sq[3] = 1
							elif (rcvdir + 1) % 4 == dir and rcvpwr in (2,3):
								sq[3] = 1
						case _: 
							if rcvdir == dir and rcvpwr == 1:
								sq[3] = 1
	G = dc(N)

#=Print=Tiles======================================================================================================

	selsq = []
	selrec = ()

	for l in G:
		for sq in l:
			if type(sq) == int:
				print('error')
			rec = pygame.Rect((10 * sq[0] + CAM[0]) * CAM[2] + og[0], (10 * sq[1] + CAM[1]) * CAM[2] + og[1], 10 * CAM[2], 10 * CAM[2])
			pygame.draw.rect(screen, (15, 15, 15), rec)

			if sq[2] > 0:
				spr = pygame.transform.scale(img(sq), (rec[2], rec[3]))

			if rec.collidepoint(mousepos[0],mousepos[1]):
				selsq = [sq[0], sq[1]]
				selrec = rec
				#print(selsq)

			if sq[2] > 0:
				screen.blit(spr, rec)
	
	if PLAY:
		if len(selrec) > 0 and G[selsq[0]][selsq[1]][2] == 6:
			spr = pygame.transform.scale(get_image('input_mask').convert_alpha(), (selrec[2], selrec[3]))
			spr = pygame.transform.rotate(spr, 90 * G[selsq[0]][selsq[1]][4])
			screen.blit(spr, selrec)
	elif SHIFT:
		srf.fill((0, 0, 0, 0))
		match len(S):
			case 0:
				if len(selrec) > 0:
					pygame.draw.rect(srf, (255, 255, 255, 32), selrec)
			case 1:
				if len(selrec) > 0:
					m0 = min(S[0][0], selsq[0])
					m1 = min(S[0][1], selsq[1])
					newrec = ((10 * m0 + CAM[0]) * CAM[2] + og[0], (10 * m1 + CAM[1]) * CAM[2] + og[1], (10 * (abs(S[0][0] - selsq[0]) + 1)) * CAM[2], (10 * (abs(S[0][1] - selsq[1]) + 1)) * CAM[2])
					pygame.draw.rect(srf, (255, 255, 255, 32), newrec)
				else:
					newrec = ((10 * S[0][0] + CAM[0]) * CAM[2] + og[0], (10 * S[0][1] + CAM[1]) * CAM[2] + og[1], 10 * CAM[2], 10 * CAM[2])
					pygame.draw.rect(srf, (255, 255, 255, 32), newrec)
			case 3:
				m0 = min(S[0][0], S[1][0])
				m1 = min(S[0][1], S[1][1])
				newrec = ((10 * m0 + CAM[0]) * CAM[2] + og[0], (10 * m1 + CAM[1]) * CAM[2] + og[1], (10 * (abs(S[0][0] - S[1][0]) + 1)) * CAM[2], (10 * (abs(S[0][1] - S[1][1]) + 1)) * CAM[2])
				pygame.draw.rect(srf, (255, 255, 255, 64), newrec)

		screen.blit(srf, (0, 0))

	else:
		pygame.draw.rect(screen, TYPES[seltype], (10, 10, 15, 15))

		#=hovering=tile=#
		if len(selrec) > 0:
			this_sq = (selsq[0], selsq[1], seltype, 0, R)
			spr = pygame.transform.scale(img(this_sq), (selrec[2], selrec[3]))
			spr.set_alpha(128)
			screen.blit(spr, selrec)

#=Save/Load========================================================================================================

	if SAVE:
		if currSave == None:
			txt = font.render('New Save: Check terminal', True, (255, 255, 255))
			screen.blit(txt, (10, 40))
			pygame.display.flip()
			nme = input('\nName of save (leave empty to cancel): ')

			if os.path.isfile(f'saves\\{nme}.txt'):
				print(f'(!) File \'saves\\{nme}.txt\' already exists')

		else:
			nme = currSave

		if nme != '':
			newSave = open(f'saves\\{nme}.txt', 'w')

			data = f'{len(G)}#{len(G[0])}'
			for coord in C:
				data += '\n'

				tl = G[coord[0]][coord[1]]
				data += f'{tl[0]} {tl[1]} {tl[2]} {tl[3]} {tl[4]}'

			newSave.write(data)
			newSave.close()
			currSave = nme
			
		pygame.event.clear()
		SAVE = False

	if LOAD:
		txt = font.render('Load: Check terminal', True, (255, 255, 255))
		screen.blit(txt, (10, 40))
		pygame.display.flip()
		nme = input('\nName of file to load (leave empty to cancel): ')

		if nme != '':
			if os.path.isfile(f'saves\\{nme}.txt'):
				C.clear()

				currSave = nme

				loadFrom = open(f'saves\\{nme}.txt', 'r')
				data = loadFrom.read().split('\n')
				loadFrom.close()

				dim = data[0].split('#')
				for i in range(2):
					dim[i] = int(dim[i])

				C.clear()
				loadedGrid = []
				for x in range(dim[0]):
					loadedGrid.append([])
					for y in range(dim[1]):
						loadedGrid[x].append([x, y, 0, 0, 0])

				for ln in data[1:]:
					d = ln.split(' ')
					for i in range(len(d)):
						d[i] = int(d[i])
					loadedGrid[d[0]][d[1]] = d
					C.append(tuple(d[:2]))

				G = dc(loadedGrid)

			else:
				print(f'(!) File saves\\{nme}.txt does not exist')

		pygame.event.clear()
		LOAD = False

	pygame.display.flip()
	del srf

#=End==============================================================================================================

pygame.quit()

#==================================================================================================================
