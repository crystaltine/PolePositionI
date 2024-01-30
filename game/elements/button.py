from pygame import Surface, Color
from CONSTANTS import *

#From 
class Button():
	
	def __init__(self, pos: tuple, display_text: str, base_color, hovering_color, image: Surface = None, disabled=False):
		"""
		`pos` should be a tuple that indicates the (x, y) position of the TOP LEFT corner of the button.
		Refer to `CONSTANTS.py` for button image size. At the time of writing, buttons are 240x60 pixels.
  
		`display_text` is the text to be displayed on the button.
  
		`base_color`: color of the text normally (hex string such as #ffffff)
		`hovering_color`: color of text on hover (hex string such as #96faff)
  
		`image`: image to be displayed as the background of the button. If `None`, then the button will be a solid color.
		
		### For `image`, it is suggested to use the constants `BUTTON_MEDIUM` and `BUTTON_LARGE`
  
		@see - https://github.com/baraltech/Menu-System-PyGame/blob/main/button.py
		"""
		self.image = image
		# use srcalpha to allow transparency
		if self.image is not None:
			self.image = self.image.convert_alpha()
			self.image.set_alpha(255 if not disabled else 100)
		self.x_pos = pos[0]
		self.y_pos = pos[1]
		self.disabled = disabled
		self.base_color, self.hovering_color = Color(base_color), Color(hovering_color)
		self.display_text = display_text
  
		self.text = FONT_MEDIUM.render(self.display_text, True, self.base_color).convert_alpha()
		self.text.set_alpha(255 if not disabled else 100)

		if self.image is None:
			self.image = self.text
		
		# let rect's top left be x_pos, y_pos
		self.rect = self.image.get_rect(topleft=(self.x_pos, self.y_pos))
		self.text_rect = self.text.get_rect(center=self.rect.center)
  
	def update_text(self, screen):
		"""
		Call this instead of `update` if you want to update the text of the button.
		"""
		self.text = FONT_MEDIUM.render(self.display_text, True, self.base_color).convert_alpha()
		self.text.set_alpha(255 if not self.disabled else 100)
		self.text_rect = self.text.get_rect(center=self.rect.center)
  
		self.update(screen)

	def update(self, screen):
		if self.image is not None:
			screen.blit(self.image, self.rect)
		screen.blit(self.text, self.text_rect)

	def is_hovering(self, position):     
		return (
			not self.disabled and # disabled buttons cannot be hovered and thus not clicked
			position[0] > self.rect.left and 
			position[0] < self.rect.right and 
			position[1] > self.rect.top and 
			position[1] < self.rect.bottom
		)

	def changeColor(self, position):
		if self.is_hovering(position):
			# we actually don't care about disabled or not since disabled buttons cannot be hovered
			self.text = FONT_MEDIUM.render(self.display_text, True, self.hovering_color)
		else:
			self.text = FONT_MEDIUM.render(self.display_text, True, self.base_color).convert_alpha()
			self.text.set_alpha(255 if not self.disabled else 100)