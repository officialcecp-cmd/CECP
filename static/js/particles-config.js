// =============================================================================
// CECP Club Website — tsParticles Configuration
// =============================================================================
// Creates the interactive "Anti-Gravity" floating network effect.
// Particles drift upward slowly, connect via lines, and react to mouse input.
// =============================================================================

async function initParticles() {
    // Load the tsParticles engine
    await loadSlim(tsParticles);

    await tsParticles.load({
        id: "tsparticles",
        options: {

            // -----------------------------------------------------------------
            // Full-screen background (transparent — sits behind hero content)
            // -----------------------------------------------------------------
            fullScreen: { enable: false },
            background: { color: { value: "transparent" } },

            // -----------------------------------------------------------------
            // Frame rate & performance
            // -----------------------------------------------------------------
            fpsLimit: 60,
            detectRetina: true,

            // -----------------------------------------------------------------
            // Mouse & touch interactivity
            // -----------------------------------------------------------------
            interactivity: {
                detectsOn: "window",
                events: {
                    onHover: {
                        enable: true,
                        mode: ["grab", "bubble"],
                        parallax: {
                            enable: true,
                            force: 40,
                            smooth: 20,
                        },
                    },
                    onClick: {
                        enable: true,
                        mode: "repulse",
                    },
                    resize: { enable: true },
                },
                modes: {
                    grab: {
                        distance: 180,
                        links: {
                            opacity: 0.45,
                            color: "#22d3ee",
                        },
                    },
                    bubble: {
                        distance: 200,
                        size: 5,
                        duration: 2,
                        opacity: 0.6,
                    },
                    repulse: {
                        distance: 250,
                        duration: 0.6,
                        speed: 0.5,
                    },
                },
            },

            // -----------------------------------------------------------------
            // Particle Configuration
            // -----------------------------------------------------------------
            particles: {
                number: {
                    value: 90,
                    density: {
                        enable: true,
                        width: 1920,
                        height: 1080,
                    },
                },

                // Colors: neon cyan and blue palette
                color: {
                    value: ["#06b6d4", "#22d3ee", "#3b82f6", "#6366f1", "#8b5cf6"],
                },

                // Shape: circles with slight variation
                shape: {
                    type: "circle",
                },

                // Opacity: subtle with gentle pulsing
                opacity: {
                    value: { min: 0.15, max: 0.55 },
                    animation: {
                        enable: true,
                        speed: 0.8,
                        startValue: "random",
                        sync: false,
                        mode: "auto",
                    },
                },

                // Size: small glowing dots
                size: {
                    value: { min: 1.2, max: 3.5 },
                    animation: {
                        enable: true,
                        speed: 1.5,
                        startValue: "random",
                        sync: false,
                        mode: "auto",
                    },
                },

                // Links: the network lines connecting particles
                links: {
                    enable: true,
                    distance: 160,
                    color: {
                        value: "#06b6d4",
                    },
                    opacity: 0.12,
                    width: 1,
                    triangles: {
                        enable: true,
                        opacity: 0.015,
                        color: { value: "#06b6d4" },
                    },
                },

                // Movement: slow, anti-gravity (upward drift)
                move: {
                    enable: true,
                    speed: { min: 0.3, max: 0.9 },
                    direction: "top",          // Anti-gravity: drift upward
                    random: true,
                    straight: false,
                    outModes: {
                        default: "out",
                        top: "out",
                        bottom: "out",
                    },
                    attract: {
                        enable: true,
                        rotate: { x: 800, y: 1200 },
                    },
                    // Gentle wobble for organic motion
                    path: {
                        enable: false,
                    },
                    warp: false,
                    spin: {
                        acceleration: 0,
                    },
                },

                // Collision: slight bounce
                collisions: {
                    enable: false,
                },

                // Shadow glow on each particle
                shadow: {
                    blur: 8,
                    color: { value: "#06b6d4" },
                    enable: true,
                    offset: { x: 0, y: 0 },
                },
            },

            // -----------------------------------------------------------------
            // Smooth entry animation
            // -----------------------------------------------------------------
            smooth: true,

            // -----------------------------------------------------------------
            // Performance: pause when not visible
            // -----------------------------------------------------------------
            pauseOnBlur: true,
            pauseOnOutsideViewport: true,
        },
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initParticles);
} else {
    initParticles();
}
