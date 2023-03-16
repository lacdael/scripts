import json

def parse_text(text):
    data = text.split("\n")
    dd_entities = []
    entity = {}
    for line in data:
        if line.startswith("DD Entity:"):
            if entity:
                dd_entities.append(entity)
                entity = {}
            entity["DD Entity"] = line.split(":")[1].strip()
        elif line.startswith("Definition:"):
            entity["Definition"] = line.split(":")[1].strip()
        elif line.startswith("Comment:"):
            entity["Comment"] = line.split(":")[1].strip()
        elif line.startswith("Typically used by Device Classes:"):
            entity["Typically used by Device Classes"] = line.split(":")[1].strip()
        elif line.startswith("Unit:"):
            entity["Unit"] = line.split(":")[1].strip()
        elif line.startswith("Resolution:"):
            entity["Resolution"] = line.split(":")[1].strip()
        elif line.startswith("SAE SPN:"):
            entity["SAE SPN"] = line.split(":")[1].strip()
        elif line.startswith("CANBus Range:"):
            entity["CANBus Range"] = line.split(":")[1].strip()
        elif line.startswith("Display Range:"):
            entity["Display Range"] = line.split(":")[1].strip()
        elif line.startswith("Submit by:"):
            entity["Submit by"] = line.split(":")[1].strip()
        elif line.startswith("Submit Date:"):
            entity["Submit Date"] = line.split(":")[1].strip()
        elif line.startswith("Submit Company:"):
            entity["Submit Company"] = line.split(":")[1].strip()
        elif line.startswith("Revision Number:"):
            entity["Revision Number"] = line.split(":")[1].strip()
        elif line.startswith("Current Status:"):
            entity["Current Status"] = line.split(":")[1].strip()
        elif line.startswith("Status Date:"):
            entity["Status Date"] = line.split(":")[1].strip()
        elif line.startswith("Status Comments:"):
            entity["Status Comments"] = line.split(":")[1].strip()
        elif line.startswith("Attachments:"):
            entity["Attachments"] = line.split(":")[1].strip()
    dd_entities.append(entity)
    return json.dumps(dd_entities, indent=2)


