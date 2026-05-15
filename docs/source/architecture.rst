Architecture
============

Overview
--------

All game objects inherit from :class:`core.circle_shape.CircleShape`, which extends
`pygame.sprite.Sprite <https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite>`_.
Each instance stores a ``position`` and ``velocity``
(both `pygame.Vector2 <https://www.pygame.org/docs/ref/math.html#pygame.math.Vector2>`_)
and a ``radius`` used for circle-circle collision detection. Subclasses must
implement :meth:`~core.circle_shape.CircleShape.draw` and
:meth:`~core.circle_shape.CircleShape.update`.

.. code-block:: text

   pygame.sprite.Sprite
   └── CircleShape          (position, velocity, radius, check_collision)
       ├── Player           (rotation, cooldown, hp, invincibility, 5-point hull)
       ├── Shot             (moves by velocity each frame; laser-bolt draw)
       └── Asteroid         (moves and rotates; jagged polygon; splits on hit)

   pygame.sprite.Sprite
   └── AsteroidField        (spawn timer; lives only in updatable group)

All five classes live in the ``core/`` package:

+------------------------------------+----------------------------------+
| Module                             | Contents                         |
+====================================+==================================+
| :mod:`core.circle_shape`           | ``CircleShape`` base class       |
+------------------------------------+----------------------------------+
| :mod:`core.asteroid`               | ``Asteroid``                     |
+------------------------------------+----------------------------------+
| :mod:`core.asteroid_field`         | ``AsteroidField``                |
+------------------------------------+----------------------------------+
| :mod:`core.player`                 | ``Player``, ``Shot``             |
+------------------------------------+----------------------------------+
| :mod:`core.constants`              | Tuneable numeric constants       |
+------------------------------------+----------------------------------+

.. seealso::

   `pygame.sprite module <https://www.pygame.org/docs/ref/sprite.html>`_
      Full reference for sprite groups and the ``Sprite`` base class.

   `pygame.math.Vector2 <https://www.pygame.org/docs/ref/math.html#pygame.math.Vector2>`_
      2-D vector used for position and velocity.

Sprite Group Wiring
-------------------

``main.py`` assigns class-level ``containers`` tuples **before** any instance is
created. :meth:`core.circle_shape.CircleShape.__init__` checks
``hasattr(self, "containers")`` and, if present, passes those groups to
`pygame.sprite.Sprite.__init__ <https://www.pygame.org/docs/ref/sprite.html#pygame.sprite.Sprite.__init__>`_,
automatically registering each new instance in the correct groups.

Four groups are used:

+-------------+-----------------------------------+
| Group       | Members                           |
+=============+===================================+
| updatable   | Player, Asteroid, AsteroidField,  |
|             | Shot                              |
+-------------+-----------------------------------+
| drawable    | Player, Asteroid, Shot            |
+-------------+-----------------------------------+
| asteroids   | Asteroid                          |
+-------------+-----------------------------------+
| shots       | Shot                              |
+-------------+-----------------------------------+

Game Loop
---------

The loop in ``main.py`` runs at **60 FPS** and follows this order each tick:

1. **Fill** the screen black.
2. **Starfield** — 180 fixed stars at seeded-random positions drawn over the
   black background.
3. **Draw** every sprite in ``drawable``.
4. **Update** every sprite in ``updatable`` (passes ``dt`` in seconds).
5. **Collision check** — asteroid vs. player (HP reduced by damage amount;
   game-over screen triggered when HP reaches 0) and asteroid vs. shot
   (shot killed, asteroid split; ``destroyed`` counter incremented).
6. **HUD** — survival timer, HP bar, and destroyed-asteroid count blit over the scene.
7. **Flip** the display buffer.

All movement and timing is multiplied by ``dt`` for frame-rate independence.

Visual Style
------------

All drawing uses pygame built-in draw primitives — no external image assets.

**Asteroids** are jagged grey-brown polygons. Each asteroid pre-computes 8–12
vertices at randomised radii (65–100 % of the collision radius) and angles on
construction. A random ``rotation_speed`` (±50 °/s) is also assigned, so every
asteroid tumbles independently as it moves.

**Player ship** is a five-point navy hull with a cyan outline, a light-blue
cockpit dot near the nose, and an orange engine glow at the rear. Holding the
thrust key draws a flickering orange/yellow flame triangle behind the ship.

**Shots** are a bright-yellow filled circle with a short golden tail line
trailing opposite the direction of travel.

**Starfield** — 180 points at fixed seeded positions — is rendered over the
black background each frame before game objects, providing depth without any
animation cost.

**HUD** — rendered last so it always appears on top — shows:

* ``Time  MM:SS`` at the top-left.
* HP bar (filled rect, green → yellow → red) with ``HP N/10`` label at the top-centre.
* ``Destroyed  N`` at the top-right.

Hit Points & Damage
-------------------

``Player`` starts with ``PLAYER_MAX_HP = 10`` hit points.  Each time an
asteroid overlaps the player's circle:

* A **large** asteroid (``radius > ASTEROID_MIN_RADIUS``) deals
  ``PLAYER_HP_DAMAGE_LARGE = 3`` damage.
* A **small** asteroid (``radius == ASTEROID_MIN_RADIUS``) deals
  ``PLAYER_HP_DAMAGE_SMALL = 1`` damage.

After taking damage :meth:`~core.player.Player.take_damage` starts a
``PLAYER_INVINCIBILITY_DURATION = 1.5`` s invincibility window during which
further collisions are ignored and the ship flashes at 4 Hz.

When HP reaches 0 ``main.py`` calls ``_game_over_screen()``, which runs its
own render loop: three expanding explosion rings emanate from the ship's
position for 1.5 s while a "GAME OVER" overlay shows the final time and kill
count.  The player can press any key to exit after 1 s.

Asteroid Splitting
------------------

When :meth:`~core.asteroid.Asteroid.split` is called the asteroid kills itself.
If its radius exceeds ``ASTEROID_MIN_RADIUS``, two children are spawned at the
same position with velocities rotated ±20–50 ° from the parent and scaled by
**1.2×**. Minimum-size asteroids are simply destroyed.

Shooting Cooldown
-----------------

``Player.cooldown`` decrements by ``dt`` every frame.
:meth:`~core.player.Player.shoot` is a no-op while ``cooldown > 0``; on success
it spawns a :class:`~core.player.Shot` and resets ``cooldown`` to
``PLAYER_SHOOT_COOLDOWN``.

Constants
---------

All tuneable values (screen size, radii, speeds, rates) live in
:mod:`core.constants` so they can be adjusted without touching game logic.

Debug Logging
-------------

:mod:`logger` provides two opt-in functions:

* :func:`~logger.log_state` — snapshots sprite group state to
  ``game_state.jsonl`` once per second for the first 16 seconds.
* :func:`~logger.log_event` — appends structured events to
  ``game_events.jsonl``.

Both files are git-ignored.

Docker
------

The provided :file:`Dockerfile` builds a ``python:3.13-slim`` image with the
SDL2 runtime libraries and installs dependencies via
`uv <https://docs.astral.sh/uv/>`_. ``SDL_AUDIODRIVER=dummy`` is set in the
image so no audio hardware is required.

To display the game window the host's X11 socket must be forwarded:

.. code-block:: bash

   xhost +local:docker
   docker run --rm \
     -e DISPLAY=$DISPLAY \
     -v /tmp/.X11-unix:/tmp/.X11-unix \
     asteroids

.. seealso::

   `SDL2 documentation <https://wiki.libsdl.org/SDL2/FrontPage>`_
      Reference for the underlying display and audio drivers.

   `Docker documentation <https://docs.docker.com/>`_
      Building and running container images.
