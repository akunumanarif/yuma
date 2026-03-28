import logging
from app.models.job import SceneStage

logger = logging.getLogger(__name__)

# Stage progression templates per category
CATEGORY_TEMPLATES = {
    "room_cleaning": [
        ("Complete Mess", "same room, extremely cluttered and messy, clothes piled on the bed and floor, books scattered, trash everywhere, a young person standing in the doorway looking overwhelmed at the mess"),
        ("Starting Cleanup", "same room, a person actively picking up clothes from the floor and gathering trash into a bag, slight improvement visible, early stage of cleaning"),
        ("Half Cleaned", "same room, a person organizing items on the desk and bookshelf, floor partially cleared of clutter, noticeable progress being made"),
        ("Mostly Clean", "same room, a person making the bed and arranging pillows, furniture clearly visible, room mostly tidy with only minor items to put away"),
        ("Fully Clean", "same room, a person doing a final wipe of the desk, room completely clean and organized, everything in place, fresh and tidy"),
        ("New Interior", "same room completely transformed, person standing proudly admiring the clean organized space, cozy and inviting atmosphere"),
    ],
    "construction": [
        ("Empty Land", "same plot of land, empty site, bare ground, construction materials and equipment nearby, workers planning the layout"),
        ("Foundation", "same site, workers laying the concrete foundation, basic structure emerging from the ground"),
        ("Framework", "same site, structural steel and wood framework erected, walls taking shape, construction crew actively working"),
        ("Walls & Roof", "same building site, walls completed, roof structure in place, workers on scaffolding finishing exterior"),
        ("Interior Work", "same building interior, workers installing windows and flooring, painting in progress, finishing work underway"),
        ("Complete Building", "same location, fully completed modern building, beautiful architecture, professional finish, surrounded by landscaping"),
    ],
    "car_cleaning": [
        ("Very Dirty Car", "same car in driveway, extremely dirty covered in mud and grime, dusty windows, a person looking at the dirty car preparing to clean"),
        ("Rinsing", "same car, a person rinsing it with a hose, water washing away surface dirt, first stage of washing"),
        ("Soap & Scrub", "same car, a person scrubbing with soapy sponge, foam covering the surface, thorough cleaning in progress"),
        ("Rinsing Off", "same car, a person rinsing off all the soap, car surface becoming visible under running water"),
        ("Drying", "same car, a person carefully drying with microfiber towels, surface gleaming, almost done"),
        ("Showroom Clean", "same car, perfectly clean and polished, person admiring the mirror-like shine, showroom condition"),
    ],
    "carpet_cleaning": [
        ("Dirty Carpet", "same carpet in same room, heavily stained and dirty, visible grime and discolored patches, a person crouching to inspect the stains"),
        ("Vacuuming", "same carpet, a person vacuuming the surface, loose dirt being removed, first stage of cleaning"),
        ("Applying Solution", "same carpet, a person applying cleaning solution to stains with spray bottle and scrub brush"),
        ("Scrubbing", "same carpet, a person scrubbing vigorously, foam forming, stains visibly lifting"),
        ("Steam Cleaning", "same carpet, a person using professional steam cleaner, carpet becoming noticeably cleaner"),
        ("Clean Carpet", "same carpet fully restored, person standing back to admire the clean result, vibrant colors and fresh appearance"),
    ],
    "garden": [
        ("Overgrown Garden", "same garden plot, completely overgrown with weeds everywhere, neglected plants, a person surveying the wild overgrown space"),
        ("Clearing", "same garden, a person pulling weeds and removing dead plants, tools in hand, clearing the space"),
        ("Soil Preparation", "same garden, a person tilling and preparing the soil, garden beds taking shape, fresh earth"),
        ("Planting", "same garden, a person planting seedlings and sowing seeds, organized garden rows visible"),
        ("Growing", "same garden, a person tending to growing plants, garden taking shape, greenery emerging"),
        ("Beautiful Garden", "same garden fully transformed, person standing in stunning landscaped garden in full bloom, colorful flowers, lush greenery"),
    ],
    "renovation": [
        ("Old Room", "same room, outdated and worn, old furniture, peeling paint, dated decor, a worker assessing what needs to change"),
        ("Demolition", "same room, worker removing old fixtures and stripping walls, renovation underway, raw state"),
        ("Structural Work", "same room, workers building new walls or structures, raw construction state, bare materials"),
        ("Painting & Flooring", "same room, worker applying fresh paint and installing new flooring, room transforming"),
        ("Fixtures & Fittings", "same room, worker installing new fixtures, lighting added, furniture being carefully placed"),
        ("Renovated Room", "same room completely renovated, worker doing final inspection, fresh modern design, beautiful new interior"),
    ],
    "other": [
        ("Before - Initial State", "same location, initial state before transformation, a person present observing the starting condition"),
        ("Early Progress", "same location, a person working, early stage of transformation, subtle changes beginning"),
        ("Quarter Way", "same location, a person actively working, transformation 25% complete, noticeable changes visible"),
        ("Halfway", "same location, a person working hard, transformation 50% complete, significant progress made"),
        ("Almost Done", "same location, a person applying final touches, transformation nearly complete"),
        ("Final Result", "same location fully transformed, person standing proudly admiring the impressive final result"),
    ],
}

STYLE_PREFIX = (
    "Photorealistic photography, DSLR camera, natural lighting, "
    "fixed wide-angle camera position, same room same perspective every shot, "
    "high detail, 8k resolution. "
)


def _build_prompt(stage_desc: str, goal: str) -> str:
    # Anchor every frame to the starting room description for visual consistency
    start_scene = goal.split("→")[0].strip() if "→" in goal else goal
    return f"{STYLE_PREFIX}Setting: {start_scene[:180]}. {stage_desc}."


async def plan_scene(goal: str, category: str, num_stages: int) -> list[SceneStage]:
    templates = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["other"])

    # Select evenly spaced stages to match num_stages
    if num_stages >= len(templates):
        selected = templates
    else:
        step = (len(templates) - 1) / (num_stages - 1)
        selected = [templates[round(i * step)] for i in range(num_stages)]

    stages = []
    for i, (title, desc) in enumerate(selected):
        strength = 0.60 if i == 1 else 0.70  # first img2img slightly lower
        stages.append(SceneStage(
            index=i,
            title=title,
            description=desc,
            prompt=_build_prompt(desc, goal),
            negative_prompt="",
            img2img_strength=strength,
        ))

    logger.info(f"Template planner: {len(stages)} stages for category '{category}'")
    return stages
