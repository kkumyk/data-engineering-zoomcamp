# Introduction to Data Engineering

Data Engineering is the design and development of systems for collecting, storing and analyzing data at scale.

## Docker & Postgres

### Creating a custom pipeline with Docker

To build the image:

```bash
docker build -t install_poetry_image_test:poetry .
```

- intall_poetry_image_test will be the name of the image
- the image tag will be poetry

Run the container and pass an argument to it, so that our pipeline will receive it:
```bash
docker run -it install_poetry_image_test:poetry 5

# Expected result:
# ['pipeline.py', '5']
# Job finished successfully! Celebrate it with 5 pizzas!
```