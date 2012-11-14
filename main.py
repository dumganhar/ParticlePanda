import kivy
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.togglebutton import ToggleButton
from kivy.factory import Factory
from kivy.uix.boxlayout import BoxLayout
from kivy.core.image import Image
from kivy.uix.image import Image as ImageWidget
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivyparticle.engine import *
from colorpicker.colorpicker import ColorPicker, ColorWheel
from kivy.properties import NumericProperty, BooleanProperty, ListProperty, StringProperty, ObjectProperty
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader
from kivy.lang import Builder
import os
import math
from random import randint

from time import sleep
from xml.dom.minidom import Document
import xml.dom.minidom


class ParticleBuilder(Widget):
    demo_particle = ObjectProperty(ParticleSystem)
    particle_window = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(ParticleBuilder, self).__init__(**kwargs)


    def on_touch_down(self, touch):
        super(ParticleBuilder, self).on_touch_down(touch)
        if self.particle_window.collide_point(touch.x, touch.y):
            self.demo_particle.emitter_x = touch.x
            self.demo_particle.emitter_y = touch.y

    def on_touch_move(self, touch):
        super(ParticleBuilder, self).on_touch_move(touch)
        if self.particle_window.collide_point(touch.x, touch.y):
            self.demo_particle.emitter_x = touch.x
            self.demo_particle.emitter_y = touch.y

class ParticleParamsLayout(Widget):

    tabs_loaded = BooleanProperty(False)

    def __init__(self,**kwargs):
        super(ParticleParamsLayout, self).__init__(**kwargs)

    def create_tabs(self):
        pbuilder = self.parent
        th1 = TabbedPanelHeader(text = 'Particle')
        th2 = TabbedPanelHeader(text = 'Behavior')
        th3 = TabbedPanelHeader(text = 'Color')
        th1.content = ParticlePanel(pbuilder)
        th2.content = BehaviorPanel(pbuilder)
        th3.content = ColorPanel(pbuilder)
        th1.font_size = self.size[0] * .036
        th2.font_size = self.size[0] * .036
        th3.font_size = self.size[0] * .036
        # self.parent.parent.create_particle_system()

        self.particle_tabs.default_tab = TabbedPanelHeader(text="default tab replaced"+str(randint(1,10000)))

        self.tabs_loaded = True
        self.particle_tabs.add_widget(th1)
        self.particle_tabs.add_widget(th2)
        self.particle_tabs.add_widget(th3)


    def get_default_tab(self):
        default_content = Default_Particle_Panel()
        return default_content

    def open_first_tab(self):
        # this should be built into kivy.
        for x in self.particle_tabs.tab_list:
            x.state = 'normal'

        FIRSTbutton = self.particle_tabs.tab_list[-1]
        FIRSTbutton.state="down"
        self.particle_tabs.switch_to(FIRSTbutton)


class ParticleLoadSaveLayout(Widget):
    new_particle = ObjectProperty(None)
    load_dir = 'templates'
   
    def __init__(self,**kwargs):
        load_particle_popup_content = LoadParticlePopupContents(self)
        self.load_particle_popup = Popup(title="Particle Effects", content=load_particle_popup_content, size_hint = (None,None), size=(512,512))

        save_particle_popup_content = SaveParticlePopupContents(self)
        self.save_particle_popup = Popup(title="Particle Effects", content=save_particle_popup_content, size_hint = (None,None), size=(512,512))

        super(ParticleLoadSaveLayout,self).__init__(**kwargs)

    def _reset_layout(self, layout):
        for w in layout.children[:]:
            if isinstance(w, Label):
                layout.remove_widget(w)

    def _load_show_filenames(self, fnames):
        layout = self.load_particle_popup.content.blayout

        self._reset_layout(layout)
        self.load_particle_popup.content.blayout_height = self.load_particle_popup.content.menu_height + 2*layout.padding + len(fnames)*(layout.spacing + self.load_particle_popup.content.label_height)

        for f in fnames:
            ctx = {'text': f, 'height': self.load_particle_popup.content.label_height, 'parent': self}
            button = Builder.template('LoadFilenameButton', **ctx)
            layout.add_widget(button)

    def open_filename(self,fname):
        self.load_particle_popup.dismiss()
        self.load_particle(name=os.path.join(self.load_dir,fname))

    def load_templates(self):
        self.load_dir = 'templates'
        self._load_show_filenames([fn for fn in os.listdir(self.load_dir) if fn.endswith('.pex')])

    def load_user_files(self):
        self.load_dir = 'user_effects'
        self._load_show_filenames([fn for fn in os.listdir(self.load_dir) if fn.endswith('.pex')])

    def show_load_popup(self):
        self.load_templates()
        self.load_particle_popup.open()

    def show_save_popup(self):
        self._save_show_filenames([fn for fn in os.listdir('user_effects') if fn.endswith('.pex')] + ['[ New file... ]'])
        self.save_particle_popup.open()

    def _save_show_filenames(self, fnames):
        layout = self.save_particle_popup.content.blayout

        self._reset_layout(layout)
        self.save_particle_popup.content.blayout_height = 2*layout.padding + len(fnames)*(layout.spacing + self.save_particle_popup.content.label_height)

        for f in fnames:
            ctx = {'text': f, 'height': self.save_particle_popup.content.label_height, 'parent': self}
            button = Builder.template('SaveFilenameButton', **ctx)
            layout.add_widget(button)

    def save_filename(self, fname):
        if fname == '[ New file... ]':
            self.new_file_popup = Popup(title="Please choose a filename.", content = GetNewFilenameLayout(self), size_hint = (None, None), size = (512,256), pos=(200,200))
            self.new_file_popup.open()
            return

        print "writing to", fname

        pbuilder = self.parent.parent
        new_particle = Document()
        particle_values = new_particle.createElement("particleEmitterConfig")
        new_particle.appendChild(particle_values)


        particle_values.appendChild(self.xml_from_attribute(new_particle, 'sourcePositionVariance', ('x', 'y'), (pbuilder.demo_particle.emitter_x_variance, pbuilder.demo_particle.emitter_y_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'gravity', ('x', 'y'), (pbuilder.demo_particle.gravity_x, pbuilder.demo_particle.gravity_y)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'emitterType', ('value'), (pbuilder.demo_particle.emitter_type)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'maxParticles', ('value'), (pbuilder.demo_particle.max_num_particles)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'particleLifeSpan', ('value'), (pbuilder.demo_particle.life_span)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'particleLifespanVariance', ('value'), (pbuilder.demo_particle.life_span_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'startParticleSize', ('value'), (pbuilder.demo_particle.start_size)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'startParticleSizeVariance', ('value'), (pbuilder.demo_particle.start_size_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'finishParticleSize', ('value'), (pbuilder.demo_particle.end_size)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'FinishParticleSizeVariance', ('value'), (pbuilder.demo_particle.end_size_variance)))
        
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'angle', ('value'), (math.degrees(pbuilder.demo_particle.emit_angle))))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'angleVariance', ('value'), (math.degrees(pbuilder.demo_particle.emit_angle_variance))))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'rotationStart', ('value'), (math.degrees(pbuilder.demo_particle.start_rotation))))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'rotationStartVariance', ('value'), (math.degrees(pbuilder.demo_particle.start_rotation_variance))))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'rotationEnd', ('value'), (math.degrees(pbuilder.demo_particle.end_rotation))))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'rotationEndVariance', ('value'), (math.degrees(pbuilder.demo_particle.end_rotation_variance))))
        
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'speed', ('value'), (pbuilder.demo_particle.speed)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'speedVariance', ('value'), (pbuilder.demo_particle.speed_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'radialAcceleration', ('value'), (pbuilder.demo_particle.radial_acceleration)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'radialAccelVariance', ('value'), (pbuilder.demo_particle.radial_acceleration_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'tangentialAcceleration', ('value'), (pbuilder.demo_particle.tangential_acceleration)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'tangentialAccelVariance', ('value'), (pbuilder.demo_particle.tangential_acceleration_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'maxRadius', ('value'), (pbuilder.demo_particle.max_radius)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'maxRadiusVariance', ('value'), (pbuilder.demo_particle.max_radius_variance)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'minRadius', ('value'), (pbuilder.demo_particle.min_radius)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'rotatePerSecond', ('value'), (math.degrees(pbuilder.demo_particle.rotate_per_second))))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'rotatePerSecondVariance', ('value'), (math.degrees(pbuilder.demo_particle.rotate_per_second_variance))))
        
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'startColor', ('red', 'green', 'blue', 'alpha'), pbuilder.demo_particle.start_color))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'startColorVariance', ('red', 'green', 'blue', 'alpha'), pbuilder.demo_particle.start_color_variance))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'finishColor', ('red', 'green', 'blue', 'alpha'), pbuilder.demo_particle.end_color))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'finishColorVariance', ('red', 'green', 'blue', 'alpha'), pbuilder.demo_particle.end_color_variance))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'blendFuncSource', ('value'), (pbuilder.demo_particle.blend_factor_source)))
        particle_values.appendChild(self.xml_from_attribute(new_particle, 'blendFuncDestination', ('value'), (pbuilder.demo_particle.blend_factor_dest)))
        
        with open(os.path.join('user_effects', fname), 'w') as outf:
            new_particle.writexml(outf, indent = "  ", newl = "\n")

        self.save_particle_popup.dismiss()
        self.save_particle_popup_content = SaveParticlePopupContents(self)

    def xml_from_attribute(self,parent, attribute, fields, values):

        xml_element = parent.createElement(attribute)
        try:
            if isinstance(fields, basestring): raise TypeError
            for idx in range(len(fields)):
                if int(float(values[idx])) == float(values[idx]):
                    val = str(int(float(values[idx])))
                else:
                    val = str(float(values[idx]))
                xml_element.setAttribute(fields[idx], val)
        except TypeError:
            if int(float(values)) == float(values):
                val = str(int(float(values)))
            else:
                val = str(float(values))
            xml_element.setAttribute(fields, val)

        return xml_element

    def load_particle(self,name='templates/fire.pex',texture_path='media/particle.png'):
        pbuilder = self.parent.parent
        pl = pbuilder.params_layout
        pw = pbuilder.particle_window

        if not pl.tabs_loaded:
            # if the default panel is loaded, we need to create tabs
            pl.create_tabs()
        else:
            # if not, then the tabs are already there, but we do need to stop and remove the particle
            pbuilder.demo_particle.stop()
            pw.remove_widget(pbuilder.demo_particle)


        new_particle = ParticleSystem(name)
        new_particle.texture = Image(texture_path).texture
        new_particle.emitter_x = pw.center_x   
        new_particle.emitter_y = pw.center_y
        pbuilder.demo_particle = new_particle
        pw.add_widget(pbuilder.demo_particle)
        pbuilder.demo_particle.start()

        pl.particle_tabs.tab_list[0].content.get_values_from_particle()
        pl.particle_tabs.tab_list[1].content.get_values_from_particle()
        pl.particle_tabs.tab_list[2].content.get_values_from_particle()
        pl.open_first_tab()
        
class GetNewFilenameLayout(Widget):
    fname_input = ObjectProperty(None)

    def __init__(self, load_save_widget, **kwargs):
        self.load_save_widget = load_save_widget
        super(GetNewFilenameLayout,self).__init__(**kwargs)

    def ok(self):
        text = self.fname_input.text[:]
        if not text.endswith('.pex'): text += '.pex'
        self.load_save_widget.save_filename(text)
        self.load_save_widget.new_file_popup.dismiss()
        

    def cancel(self):
        self.fname_input.text = 'effect.pex'
        self.load_save_widget.new_file_popup.dismiss()
        

class LoadParticlePopupContents(Widget):
    blayout = ObjectProperty(None)
    blayout_height = NumericProperty(50)
    menu_height = NumericProperty(50)
    label_height = NumericProperty(50)

    def __init__(self, load_save_widget, **kwargs):
        self.load_save_widget = load_save_widget
        super(LoadParticlePopupContents,self).__init__(**kwargs)

    def button_callback(self,value):
        if value == 'load templates':
            self.load_save_widget.load_templates()
        elif value == 'load user files':
            self.load_save_widget.load_user_files()

class SaveParticlePopupContents(Widget):
    blayout = ObjectProperty(None)
    blayout_height = NumericProperty(50)
    label_height = NumericProperty(30)

    def __init__(self, load_save_widget, **kwargs):
        self.load_save_widget = load_save_widget
        super(SaveParticlePopupContents,self).__init__(**kwargs)


class Default_Particle_Panel(Widget):
    pass

class ImageChooserCell(Widget):
    image_location = StringProperty("None")
    image_chooser = ObjectProperty(None)

    def cell_press(self):
        self.image_chooser.select(self.image_location)


class ImageChooserPopupContent(GridLayout):
    def __init__(self, image_chooser = None, **kwargs):
        super(ImageChooserPopupContent,self).__init__(rows = 8, cols = 8, col_force_default = True, row_force_default = True, row_default_height = 64, col_default_width = 64, **kwargs)
        self.image_chooser = image_chooser
        png_files = self.get_all_images('.', '.png')
        # atlasses = self.get_all_images('.', '.atlas')
        for i in png_files:
            self.add_widget(ImageChooserCell(image_location=i, image_chooser = self.image_chooser))
        

    def get_all_images(self,dir_name,extension):
        outputList = []
        for root, dirs, files in os.walk(dir_name):
            for fl in files:
                if fl.endswith(extension): outputList.append(os.path.join(root,fl))
        return outputList

    # # not yet implemented:
    # def get_image_urls_from_atlas(self,atlas_file):
    #     pass

class ImageChooser(Widget):
    button_text = StringProperty("Choose a texture...")
    image_location = StringProperty('media/particle.png')
    
    def __init__(self,**kwargs):
        image_chooser_popup_content = ImageChooserPopupContent(image_chooser = self)
        self.image_chooser_popup = Popup(title="Images", content=image_chooser_popup_content, size_hint = (None,None), size=(512,512))
        super(ImageChooser,self).__init__(**kwargs)

    def button_callback(self,):
        self.image_chooser_popup.open()

    def select(self,image_location):
        self.image_location = image_location
        self.image_chooser_popup.dismiss()


class Particle_Property_Slider(Widget):
    slider_bounds_min = NumericProperty(0)
    slider_bounds_max = NumericProperty(100)
    slider_bounds_init_value = NumericProperty(0)
    slider_step = NumericProperty(1.0)

class Particle_Color_Sliders(Widget):
    color_r = NumericProperty(1.)
    color_r_min = NumericProperty(0)
    color_r_max = NumericProperty(1.)
    color_g = NumericProperty(1.)
    color_g_min = NumericProperty(0)
    color_g_max = NumericProperty(1.)
    color_b = NumericProperty(1.)
    color_b_min = NumericProperty(0)
    color_b_max = NumericProperty(1.)
    color_a = NumericProperty(1.)
    color_a_min = NumericProperty(0)
    color_a_max = NumericProperty(1.)

    # necessary because of weird slider bug that allows values to go over bounds
    def clip(self, val, vmin, vmax):
        if val < vmin:
            return vmin
        elif val > vmax:
            return vmax
        else:
            return val

class ParticlePanel(Widget):
    particle_builder = ObjectProperty(None)
    texture_location = StringProperty("media/particle.png")
    max_num_particles = NumericProperty(200.)
    max_num_particles_min = NumericProperty(1.)
    max_num_particles_max = NumericProperty(500.)
    life_span = NumericProperty(2.)
    life_span_min = NumericProperty(.01)
    life_span_max = NumericProperty(10.)
    life_span_variance = NumericProperty(0.)
    life_span_variance_min = NumericProperty(0.)
    life_span_variance_max = NumericProperty(10.)
    start_size = NumericProperty(8.)
    start_size_min = NumericProperty(0.)
    start_size_max = NumericProperty(256.)
    start_size_variance = NumericProperty(0.)
    start_size_variance_min = NumericProperty(0.)
    start_size_variance_max = NumericProperty(256.)
    end_size = NumericProperty(8.)
    end_size_min = NumericProperty(0.)
    end_size_max = NumericProperty(256.)
    end_size_variance = NumericProperty(0.)
    end_size_variance_min = NumericProperty(0.)
    end_size_variance_max = NumericProperty(256.)
    emit_angle = NumericProperty(0.)
    emit_angle_min = NumericProperty(0.)
    emit_angle_max = NumericProperty(360.)
    emit_angle_variance = NumericProperty(0.)
    emit_angle_variance_min = NumericProperty(0.)
    emit_angle_variance_max = NumericProperty(360.)
    start_rotation = NumericProperty(0.)
    start_rotation_min = NumericProperty(0.)
    start_rotation_max = NumericProperty(360.)
    start_rotation_variance = NumericProperty(0.)
    start_rotation_variance_min = NumericProperty(0.)
    start_rotation_variance_max = NumericProperty(360.)
    end_rotation = NumericProperty(0.)
    end_rotation_min = NumericProperty(0.)
    end_rotation_max = NumericProperty(360.)
    end_rotation_variance = NumericProperty(0.)
    end_rotation_variance_min = NumericProperty(0.)
    end_rotation_variance_max = NumericProperty(360.)

    def __init__(self, pbuilder, **kwargs):
        super(ParticlePanel, self).__init__(**kwargs)
        self.particle_builder = pbuilder.parent

    def on_max_num_particles(self, instance, value):
        self.particle_builder.demo_particle.max_num_particles = value

    def on_life_span(self, instance, value):
        self.particle_builder.demo_particle.life_span = value

    def on_life_span_variance(self, instance, value):
        self.particle_builder.demo_particle.life_span_variance = value

    def on_start_size(self, instance, value):
        self.particle_builder.demo_particle.start_size = value

    def on_start_size_variance(self, instance, value):
        self.particle_builder.demo_particle.start_size_variance = value

    def on_end_size(self, instance, value):
        self.particle_builder.demo_particle.end_size = value

    def on_end_size_variance(self, instance, value):
        self.particle_builder.demo_particle.end_size_variance = value

    def on_emit_angle(self, instance, value):
        self.particle_builder.demo_particle.emit_angle = value * 0.0174532925

    def on_emit_angle_variance(self, instance, value):
        self.particle_builder.demo_particle.emit_angle_variance = value * 0.0174532925

    def on_start_rotation(self, instance, value):
        self.particle_builder.demo_particle.start_rotation = value * 0.0174532925

    def on_start_rotation_variance(self, instance, value):
        self.particle_builder.demo_particle.start_rotation_variance = value * 0.0174532925

    def on_end_rotation(self, instance, value):
        self.particle_builder.demo_particle.end_rotation = value * 0.0174532925

    def on_end_rotation_variance(self, instance, value):
        self.particle_builder.demo_particle.end_rotation_variance = value * 0.0174532925

    def on_texture_location(self,instance,value):
        self.particle_builder.demo_particle.texture = Image(value).texture

    def get_values_from_particle(self):
        properties = ['max_num_particles', 'life_span', 'life_span_variance', 'start_size', 'start_size_variance', 
                    'end_size', 'end_size_variance', 'emit_angle', 'emit_angle_variance', 'start_rotation', 
                    'start_rotation_variance', 'end_rotation', 'end_rotation_variance']
    
        for p in properties:
            if p in ['emit_angle', 'emit_angle_variance', 'start_rotation', 
                    'start_rotation_variance', 'end_rotation', 'end_rotation_variance']:
                setattr(self,p,getattr(self.particle_builder.demo_particle,p) / 0.0174532925 )
            else:
                setattr(self,p,getattr(self.particle_builder.demo_particle,p))

class BehaviorPanel(Widget):
    particle_builder = ObjectProperty(None)
    emitter_type = NumericProperty(0)

    ## Gravity Emitter Params
    emitter_x_variance = NumericProperty(0.)
    emitter_x_variance_min = NumericProperty(0.)
    emitter_x_variance_max = NumericProperty(200.)
    emitter_y_variance = NumericProperty(0.)
    emitter_y_variance_min = NumericProperty(0.)
    emitter_y_variance_max = NumericProperty(200.)
    gravity_x = NumericProperty(0)
    gravity_x_min = NumericProperty(-1500)
    gravity_x_max = NumericProperty(1500)
    gravity_y = NumericProperty(0)
    gravity_y_min = NumericProperty(-1500)
    gravity_y_max = NumericProperty(1500)
    speed = NumericProperty(0.)
    speed_min = NumericProperty(0.)
    speed_max = NumericProperty(300.)
    speed_variance = NumericProperty(0.)
    speed_variance_min = NumericProperty(0.)
    speed_variance_max = NumericProperty(300.)
    radial_acceleration = NumericProperty(0)
    radial_acceleration_min = NumericProperty(-400)
    radial_acceleration_max = NumericProperty(400)
    radial_acceleration_variance = NumericProperty(0.)
    radial_acceleration_variance_min = NumericProperty(0.)
    radial_acceleration_variance_max = NumericProperty(400.)
    tangential_acceleration = NumericProperty(0)
    tangential_acceleration_min = NumericProperty(-500)
    tangential_acceleration_max = NumericProperty(500)
    tangential_acceleration_variance = NumericProperty(0.)
    tangential_acceleration_variance_min = NumericProperty(0.)
    tangential_acceleration_variance_max = NumericProperty(500.)

    ## Radial Emitter Params
    max_radius = NumericProperty(100.)
    max_radius_min = NumericProperty(0.)
    max_radius_max = NumericProperty(250.)
    max_radius_variance = NumericProperty(0.)
    max_radius_variance_min = NumericProperty(0.)
    max_radius_variance_max = NumericProperty(250.)
    min_radius = NumericProperty(0.)
    min_radius_min = NumericProperty(0.)
    min_radius_max = NumericProperty(250.)
    rotate_per_second = NumericProperty(0)
    rotate_per_second_min = NumericProperty(-720)
    rotate_per_second_max = NumericProperty(720)
    rotate_per_second_variance = NumericProperty(0.)
    rotate_per_second_variance_min = NumericProperty(0.)
    rotate_per_second_variance_max = NumericProperty(720.)

    def __init__(self, pbuilder, **kwargs):
        super(BehaviorPanel, self).__init__(**kwargs)
        self.particle_builder = pbuilder.parent

    def set_emitter_type(self, num_type):
        self.emitter_type = num_type

    def on_emitter_type(self, instance, value):
        self.particle_builder.demo_particle.emitter_type = value

    def on_emitter_x_variance(self, instance, value):
        self.particle_builder.demo_particle.emitter_x_variance = value

    def on_emitter_y_variance(self, instance, value):
        self.particle_builder.demo_particle.emitter_y_variance = value

    def on_gravity_x(self, instance, value):
        self.particle_builder.demo_particle.gravity_x = value

    def on_gravity_y(self, instance, value):
        self.particle_builder.demo_particle.gravity_y = value

    def on_speed(self, instance, value):
        self.particle_builder.demo_particle.speed = value

    def on_speed_variance(self, instance, value):
        self.particle_builder.demo_particle.speed_variance = value

    def on_radial_acceleration(self, instance, value):
        self.particle_builder.demo_particle.radial_acceleration = value

    def on_radial_acceleration_variance(self, instance, value):
        self.particle_builder.demo_particle.tangential_acceleration_variance = value

    def on_tangential_acceleration(self, instance, value):
        self.particle_builder.demo_particle.tangential_acceleration = value

    def on_tangential_acceleration_variance(self, instance, value):
        self.particle_builder.demo_particle.tangential_acceleration_variance = value

    def on_max_radius(self, instance, value):
        self.particle_builder.demo_particle.max_radius = value

    def on_max_radius_variance(self, instance, value):
        self.particle_builder.demo_particle.max_radius_variance = value

    def on_min_radius(self, instance, value):
        self.particle_builder.demo_particle.min_radius = value

    def on_rotate_per_second(self, instance, value):
        self.particle_builder.demo_particle.rotate_per_second = math.radians(value)

    def on_rotate_per_second_variance(self, instance, value):
        self.particle_builder.demo_particle.rotate_per_second_variance = math.radians(value)

    def get_values_from_particle(self):
        properties = ['emitter_x_variance', 'emitter_y_variance', 'gravity_x', 'gravity_y', 'speed', 'speed_variance',
                     'radial_acceleration', 'radial_acceleration_variance', 'tangential_acceleration', 
                     'tangential_acceleration_variance', 'max_radius', 'max_radius_variance', 'min_radius', 
                     ]

        for p in properties:
            setattr(self,p,getattr(self.particle_builder.demo_particle,p))

        angle_properties = ['rotate_per_second', 'rotate_per_second_variance']
        for p in angle_properties:
            setattr(self,p,math.degrees(getattr(self.particle_builder.demo_particle,p)))

        if self.particle_builder.demo_particle.emitter_type == 0:
            self.gravity_button.state='down'
        elif self.particle_builder.demo_particle.emitter_type == 1:
            self.radial_button.state='down'


class ColorPanel(Widget):
    particle_builder = ObjectProperty(None)

    start_color = ListProperty([1,1,1,1])
    end_color = ListProperty([1,1,1,1])
    start_color_r_variance = NumericProperty(.1)
    start_color_r_variance_min = NumericProperty(0)
    start_color_r_variance_max = NumericProperty(1.)
    start_color_g_variance = NumericProperty(.1)
    start_color_g_variance_min = NumericProperty(0)
    start_color_g_variance_max = NumericProperty(1.)
    start_color_b_variance = NumericProperty(.1)
    start_color_b_variance_min = NumericProperty(0)
    start_color_b_variance_max = NumericProperty(1.)
    start_color_a_variance = NumericProperty(.1)
    start_color_a_variance_min = NumericProperty(0)
    start_color_a_variance_max = NumericProperty(1.)
    end_color_r_variance = NumericProperty(.1)
    end_color_r_variance_min = NumericProperty(0)
    end_color_r_variance_max = NumericProperty(1.)
    end_color_g_variance = NumericProperty(.1)
    end_color_g_variance_min = NumericProperty(0)
    end_color_g_variance_max = NumericProperty(1.)
    end_color_b_variance = NumericProperty(.1)
    end_color_b_variance_min = NumericProperty(0)
    end_color_b_variance_max = NumericProperty(1.)
    end_color_a_variance = NumericProperty(.1)
    end_color_a_variance_min = NumericProperty(0)
    end_color_a_variance_max = NumericProperty(1.)

    def __init__(self, pbuilder, **kwargs):
        super(ColorPanel, self).__init__(**kwargs)
        self.particle_builder = pbuilder.parent



    def on_start_color(self, instance, value):
        self.particle_builder.demo_particle.start_color = value

    def on_end_color(self, instance, value):
        self.particle_builder.demo_particle.end_color = value

    def on_start_color_r_variance(self, instance, value):
        self.particle_builder.demo_particle.start_color_variance[0] = self.start_color_r_variance

    def on_start_color_g_variance(self, instance, value):
        self.particle_builder.demo_particle.start_color_variance[1] = self.start_color_g_variance

    def on_start_color_b_variance(self, instance, value):
        self.particle_builder.demo_particle.start_color_variance[2] = self.start_color_b_variance

    def on_start_color_a_variance(self, instance, value):
        self.particle_builder.demo_particle.start_color_variance[3] = self.start_color_a_variance

    def on_end_color_r_variance(self, instance, value):
        self.particle_builder.demo_particle.end_color_variance[0] = self.end_color_r_variance

    def on_end_color_g_variance(self, instance, value):
        self.particle_builder.demo_particle.end_color_variance[1] = self.end_color_g_variance

    def on_end_color_b_variance(self, instance, value):
        self.particle_builder.demo_particle.end_color_variance[2] = self.end_color_b_variance

    def on_end_color_a_variance(self, instance, value):
        self.particle_builder.demo_particle.end_color_variance[3] = self.end_color_a_variance

    def get_values_from_particle(self):
        self.start_color_picker.selected_color = self.particle_builder.demo_particle.start_color
        self.start_color_variation_sliders.color_r_slider.value = self.particle_builder.demo_particle.start_color_variance[0]
        self.start_color_variation_sliders.color_g_slider.value = self.particle_builder.demo_particle.start_color_variance[1]
        self.start_color_variation_sliders.color_b_slider.value = self.particle_builder.demo_particle.start_color_variance[2]
        self.start_color_variation_sliders.color_a_slider.value = self.particle_builder.demo_particle.start_color_variance[3]
        self.end_color_picker.selected_color = self.particle_builder.demo_particle.end_color
        self.end_color_variation_sliders.color_r_slider.value = self.particle_builder.demo_particle.end_color_variance[0]
        self.end_color_variation_sliders.color_g_slider.value = self.particle_builder.demo_particle.end_color_variance[1]
        self.end_color_variation_sliders.color_b_slider.value = self.particle_builder.demo_particle.end_color_variance[2]
        self.end_color_variation_sliders.color_a_slider.value = self.particle_builder.demo_particle.end_color_variance[3]


class DebugPanel(Widget):
    fps = StringProperty(None)

    def update_fps(self,dt):
        self.fps = str(int(Clock.get_rfps()))
        Clock.schedule_once(self.update_fps)

class VariableDescriptions(Widget):
    
    def tab_info(self):
        self.description_tab = TabbedPanel()
        particle_info = TabbedPanelHeader(text = 'Particle')
        behavior_info = TabbedPanelHeader(text = 'Behavior')
        color_info = TabbedPanelHeader(text = 'Color')
        particle_info.font_size = self.size[0]*.28
        behavior_info.font_size = self.size[0]*.28
        color_info.font_size = self.size[0]*.28
        self.description_tab.default_tab = particle_info
        self.description_tab.tab_width = self.size[0]*4.36
        self.description_tab.tab_height = self.size[1]*.7
        # particle_info.content = 'nothing'
        # behavior_info.content = 'nothing'
        # color_info.content = 'nothing'
        self.description_tab.add_widget(particle_info)
        self.description_tab.add_widget(behavior_info)
        self.description_tab.add_widget(color_info)
        self.description_popup = Popup(title="Variable Descriptions", content = self.description_tab, size_hint = (.8,.8))
        self.description_popup.open()

Factory.register('ParticleBuilder', ParticleBuilder)
Factory.register('ParticleLoadSaveLayout', ParticleLoadSaveLayout)
Factory.register('ParticleParamsLayout', ParticleParamsLayout)
Factory.register('ParticlePanel', ParticlePanel)
Factory.register('BehaviorPanel', BehaviorPanel)
Factory.register('ColorPanel', ColorPanel)
Factory.register('Particle_Property_Slider', Particle_Property_Slider)
Factory.register('Particle_Color_Sliders', Particle_Color_Sliders)
Factory.register('ImageChooser', ImageChooser)
Factory.register('ColorPicker', ColorPicker)
Factory.register('ColorWheel', ColorWheel)
Factory.register('DebugPanel', DebugPanel)
Factory.register('VariableDescriptions', VariableDescriptions)
Builder.load_file('colorpicker/colorpicker.kv')

class ParticleBuilderApp(App):
    def build(self):
        pass

if __name__ == '__main__':
    ParticleBuilderApp().run()

