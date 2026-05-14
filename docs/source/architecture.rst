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
       ├── Player           (rotation, cooldown, triangle rendering)
       ├── Shot             (moves by velocity each frame)
       └── Asteroid         (moves by velocity; splits on hit)

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
2. **Draw** every sprite in ``drawable``.
3. **Update** every sprite in ``updatable`` (passes ``dt`` in seconds).
4. **Collision check** — asteroid vs. player (game over) and asteroid vs. shot
   (shot killed, asteroid split).
5. **Flip** the display buffer.

All movement and timing is multiplied by ``dt`` for frame-rate independence.

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
