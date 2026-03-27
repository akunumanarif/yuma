import logging
from app.models.job import SceneStage

logger = logging.getLogger(__name__)

# Stage progression templates per category
CATEGORY_TEMPLATES = {
    "room_cleaning": [
        ("Complete Mess", "extremely cluttered and dirty, clothes piled everywhere, trash on floor, complete disorder"),
        ("Starting Cleanup", "beginning to clean, some items being sorted, trash bags visible, slight improvement"),
        ("Half Cleaned", "room half cleaned, floor partially visible, items being organized, progress visible"),
        ("Mostly Clean", "mostly clean room, furniture visible, items organized, only minor clutter remains"),
        ("Fully Clean", "completely clean and tidy room, everything in place, fresh and organized"),
        ("New Interior", "clean modern room with new decor, stylish furniture arrangement, beautiful interior design"),
    ],
    "construction": [
        ("Empty Land", "empty plot of land or demolished site, bare ground, construction materials nearby"),
        ("Foundation", "foundation being laid, concrete work in progress, basic structure emerging"),
        ("Framework", "structural framework erected, walls taking shape, construction crew working"),
        ("Walls & Roof", "walls completed, roof structure in place, building taking final shape"),
        ("Interior Work", "interior finishing work, windows installed, painting and flooring in progress"),
        ("Complete Building", "fully completed modern building, beautiful architecture, professional finish"),
    ],
    "car_cleaning": [
        ("Very Dirty Car", "extremely dirty car covered in mud and grime, dusty windows, neglected exterior"),
        ("Rinsing", "car being rinsed with water, dirt starting to wash off, hose spraying"),
        ("Soap & Scrub", "car being scrubbed with soap and sponge, foam covering the surface"),
        ("Rinsing Off", "soap being rinsed off, car surface becoming visible, water running clean"),
        ("Drying", "car being dried with microfiber towels, surface gleaming, almost done"),
        ("Showroom Clean", "perfectly clean and polished car, mirror-like shine, showroom condition"),
    ],
    "carpet_cleaning": [
        ("Dirty Carpet", "heavily stained and dirty carpet, visible grime, discolored patches throughout"),
        ("Vacuuming", "carpet being vacuumed, loose dirt being removed, vacuum cleaner in action"),
        ("Applying Solution", "cleaning solution being applied to stains, spray bottle and scrub brush visible"),
        ("Scrubbing", "carpet being scrubbed vigorously, foam forming, stains lifting"),
        ("Steam Cleaning", "professional steam cleaner extracting dirt, carpet becoming visibly cleaner"),
        ("Clean Carpet", "perfectly clean carpet, vibrant colors restored, fresh and spotless appearance"),
    ],
    "garden": [
        ("Overgrown Garden", "completely overgrown garden, weeds everywhere, neglected plants, wild vegetation"),
        ("Clearing", "garden being cleared, dead plants removed, weeds being pulled, tools in use"),
        ("Soil Preparation", "soil being tilled and prepared, garden beds taking shape, fresh earth"),
        ("Planting", "new plants being planted, seeds being sown, organized garden rows visible"),
        ("Growing", "plants growing well, garden taking shape, greenery emerging, tended appearance"),
        ("Beautiful Garden", "stunning landscaped garden in full bloom, colorful flowers, lush greenery"),
    ],
    "renovation": [
        ("Old Room", "outdated and worn room, old furniture, peeling paint, dated decor"),
        ("Demolition", "renovation in progress, old fixtures being removed, walls being stripped"),
        ("Structural Work", "new walls or structures being built, raw construction state, bare materials"),
        ("Painting & Flooring", "fresh paint being applied, new flooring being installed, room transforming"),
        ("Fixtures & Fittings", "new fixtures installed, lighting added, furniture being placed"),
        ("Renovated Room", "completely renovated modern room, fresh design, beautiful new interior"),
    ],
    "other": [
        ("Before - Initial State", "initial state before transformation, starting condition"),
        ("Early Progress", "early stage of transformation, subtle changes beginning"),
        ("Quarter Way", "transformation 25% complete, noticeable changes visible"),
        ("Halfway", "transformation 50% complete, significant progress made"),
        ("Almost Done", "transformation nearly complete, final touches being applied"),
        ("Final Result", "transformation fully complete, impressive final result"),
    ],
}

STYLE_PREFIX = (
    "Photorealistic photography, DSLR camera, natural lighting, "
    "fixed camera angle, wide shot, high detail, 8k resolution. "
)


def _build_prompt(stage_desc: str, goal: str) -> str:
    # Extract scene context from the goal (first part before →)
    scene_context = goal.split("→")[0].strip() if "→" in goal else goal
    # Keep it concise — just combine style + stage description + scene context
    return f"{STYLE_PREFIX}{stage_desc}. Scene: {scene_context[:120]}."


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
