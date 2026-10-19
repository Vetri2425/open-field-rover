.PHONY: build up shell down sim clean logs help

help:
	@echo "open-field-rover - Phase 1 Commands"
	@echo ""
	@echo "make build        - Build Docker image"
	@echo "make up           - Start container and services"
	@echo "make shell        - Open interactive shell in container"
	@echo "make sim          - Build workspace and launch Gazebo simulation"
	@echo "make down         - Stop and remove container"
	@echo "make clean        - Clean build artifacts"
	@echo "make logs         - View container logs"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "✓ Container started. Access noVNC at http://localhost:6080"
	@echo "✓ VNC available at localhost:5900"

shell:
	docker-compose exec ros bash

sim:
	docker-compose exec ros bash -c "\
		source /opt/ros/jazzy/setup.bash && \
		colcon build --symlink-install && \
		source install/setup.bash && \
		ros2 launch ofr_gazebo spawn_rover.launch.py"

down:
	docker-compose down

clean:
	rm -rf build install log .colcon
	docker-compose down -v

logs:
	docker-compose logs -f ros
