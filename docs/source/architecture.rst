Architecture
============

Overview
--------

All game objects inherit from :class:`circleshape.CircleShape`, which extends
``pygame.sprite.Sprite``. Each instance stores a ``position`` and ``velocity``
(both ``pygame.Vector2``) and a ``radius`` used for circle-circle collision
detection. Subclasses must implement :meth:`~circleshape.CircleShape.draw` and
:meth:`~circleshape.CircleShape.update`.

.. code-block:: text

   pygame.sprite.Sprite
   └── CircleShape          (position, velocity, radius, check_collision)
       ├── Player           (rotation, cooldown, triangle rendering)
       ├── Shot             (moves by velocity each frame)
       └── Asteroid         (moves by velocity; splits on hit)

   pygame.sprite.Sprite
   └── AsteroidField        (spawn timer; lives only in updatable group)

Sprite Group Wiring
-------------------

``main.py`` assigns class-level ``containers`` tuples **before** any instance is
created. ``CircleShape.__init__`` checks ``hasattr(self, "containers")`` and, if
present, passes those groups to ``pygame.sprite.Sprite.__init__``, automatically
registering each new instance in the correct groups.

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

When :meth:`~asteroid.Asteroid.split` is called the asteroid kills itself.
If its radius exceeds ``ASTEROID_MIN_RADIUS``, two children are spawned at the
same position with velocities rotated ±20–50 ° from the parent and scaled by
**1.2×**. Minimum-size asteroids are simply destroyed.

Shooting Cooldown
-----------------

``Player.cooldown`` decrements by ``dt`` every frame. :meth:`~player.Player.shoot`
is a no-op while ``cooldown > 0``; on success it spawns a :class:`~player.Shot`
and resets ``cooldown`` to ``PLAYER_SHOOT_COOLDOWN``.

Constants
---------

All tuneable values (screen size, radii, speeds, rates) live in
:mod:`constants` so they can be adjusted without touching game logic.

Debug Logging
-------------

:mod:`logger` provides two opt-in functions:

* :func:`~logger.log_state` — snapshots sprite group state to
  ``game_state.jsonl`` once per second for the first 16 seconds.
* :func:`~logger.log_event` — appends structured events to
  ``game_events.jsonl``.

Both files are git-ignored.
