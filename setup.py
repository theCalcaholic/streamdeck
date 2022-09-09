from distutils.core import setup

setup(name='StreamDeck',
      version='0.1',
      description='Launch streaming websites right from Steam',
      author='Tobias Knöppler',
      url='https://github.com/theCalcaholic/streamdeck.git',
      packages=['streamdeck', 'streamdeck.gui', 'streamdeck.config', 'streamdeck.kiosk', 'streamdeck.steam'],
      package_data={'streamdeck.gui': ['*.kv'], 'streamdeck.kiosk': ['*.jinja2']}

      #install_requires=[
      #      'jinja2>=3.1.2,<4.0',
      #      'kivy[base]>=2.1.0,<3.0',
      #      'vdf>=3.4,<4',
      #      'appdirs>=1.4.4,<2.0']
      )
