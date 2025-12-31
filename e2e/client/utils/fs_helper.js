import { parse } from "csv-parse/sync";
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

export const fs_parse_csv = (file_path) => {
    try {
        const parsed_data = parse(fs.readFileSync(file_path, "utf-8"), {
            columns: true,
            skip_empty_lines: true,
        });
        return parsed_data;
    } catch (error) {
        console.error(`Error reading or parsing CSV file at ${file_path}:`, error);
        return [];
    }
}
