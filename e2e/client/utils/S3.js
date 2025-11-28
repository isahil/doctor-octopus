import fs from "fs";
import path from "path";
import {
	GetObjectCommand,
	ListObjectsCommand,
	PutObjectCommand,
	S3Client,
} from "@aws-sdk/client-s3";
import {
	get_aws_sdet_bucket_name,
	get_aws_sdet_bucket_region,
	get_aws_sdet_bucket_access_key_id,
	get_aws_sdet_bucket_secret_access_key,
} from "./env_loader.js";

const bucketName = get_aws_sdet_bucket_name();
const region = get_aws_sdet_bucket_region();
const accessKeyId = get_aws_sdet_bucket_access_key_id();
const secretAccessKey = get_aws_sdet_bucket_secret_access_key();

const S3_Client = new S3Client({
	credentials: { accessKeyId, secretAccessKey },
	region,
});

export async function list_objects() {
	const params = {
		Bucket: "doctor-octopus",
		Prefix: "test_reports/",
	};

	const command = new ListObjectsCommand(params);
	const response = await S3_Client.send(command);
	return response;
}

export async function get_object(imageName) {
	const params = {
		Bucket: bucketName,
		Key: imageName,
	};

	const command = new GetObjectCommand(params);
	const response = await S3_Client.send(command);
	// console.log(`Get S3 response ::: ${JSON.stringify(response)}`);
	return response;
}

export async function upload_file(bucket_name, key, file_content, content_type) {
	const params = {
		Bucket: bucket_name,
		Key: key,
		Body: file_content,
		ContentType: content_type,
	};

	const command = new PutObjectCommand(params);
	return await S3_Client.send(command);
}

export const upload_directory = async (bucket_name, local_dir_path, s3_dir_path) => {
	console.log(`Uploading directory: '${local_dir_path}' to S3 bucket ${bucket_name} > bucket directory: ${s3_dir_path}`);
	const report_dir = fs.readdirSync(local_dir_path);

	for (const r_item of report_dir) {
		const r_item_path = path.join(local_dir_path, r_item);
		const stats = fs.statSync(r_item_path);

		if (stats.isFile()) {
			const file_content = fs.readFileSync(r_item_path);
			const content_type = is_zip_file_by_extension(r_item)
				? "application/zip"
				: "application/octet-stream";
			await upload_file(bucket_name, `${s3_dir_path}/${r_item}`, file_content, content_type);
		} else if (stats.isDirectory()) {
			await upload_directory(bucket_name, r_item_path, `${s3_dir_path}/${r_item}`);
		}
	}
};

function is_zip_file_by_extension(filePath) {
	return path.extname(filePath).toLowerCase() === ".zip";
}
