import cloudinary
import cloudinary.uploader

class UploadFileService:
    """
    A service class for uploading files to Cloudinary.

    This class provides methods for configuring Cloudinary and uploading files, 
    with default settings for resizing avatars.

    Attributes:
        DEFAULT_AVATAR_HEIGHT (int): Default height for avatar images. Default is 250 pixels.
        DEFAULT_AVATAR_WIDTH (int): Default width for avatar images. Default is 250 pixels.
    """

    DEFAULT_AVATAR_HEIGHT: int = 250
    DEFAULT_AVATAR_WIDTH: int = 250

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initialize the UploadFileService with Cloudinary configuration.

        Args:
            cloud_name (str): The Cloudinary cloud name.
            api_key (str): The Cloudinary API key.
            api_secret (str): The Cloudinary API secret.

        Example:
            >>> service = UploadFileService("my_cloud_name", "my_api_key", "my_api_secret")
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Upload a file to Cloudinary and generate a resized URL.

        The uploaded file is stored with a public ID that includes the username. The
        resulting image URL is resized to the default avatar dimensions (250x250 pixels)
        and cropped to fill the specified size.

        Args:
            file: The file to upload. This should be a file-like object with a `.file` attribute.
            username (str): The username to use for the public ID in Cloudinary.

        Returns:
            str: The URL of the uploaded and resized file.

        Example:
            >>> file_url = UploadFileService.upload_file(my_file, "username123")
            >>> print(file_url)
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=UploadFileService.DEFAULT_AVATAR_WIDTH,
            height=UploadFileService.DEFAULT_AVATAR_HEIGHT,
            crop="fill",
            version=r.get("version"),
        )
        return src_url