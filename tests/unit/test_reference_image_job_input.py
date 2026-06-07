from avatar_engine.jobs.service import JobService


def test_reference_image_is_stored_as_job_parameter(settings, sample_reference_image, sample_audio) -> None:
    job_id = JobService(settings).create_talking_head_job(
        reference_image=str(sample_reference_image),
        audio=str(sample_audio),
    )
    job = JobService(settings).repository.get_job(job_id)

    assert job.input_json["reference_image_path"] == str(sample_reference_image)
    assert job.input_json["reference_image_mode"] == "job_input"
