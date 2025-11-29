import fs from "fs";

export const ensure_dir = (dir) => {
	try {
		if (!fs.existsSync(dir)) {
			fs.mkdirSync(dir, { recursive: true });
			return true;
		} else {
            console.log(`Directory already exists: ${dir}`);
        }
	} catch (error) {
		console.error(`Error ensuring directory ${dir}:`, error);
		return false;
	}
	return false;
};
